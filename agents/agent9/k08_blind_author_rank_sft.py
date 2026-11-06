"""Masked historical-author ranker; source-only controls and original K08 check.
Run in workplace-v2. Requires torch and transformers for non-smoke use.
"""
import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
CASES = (2, 6, 17, 18, 0)
CREW_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ROLE = {
    2: "First draft for a crew common-area board: human handover after a watch.",
    6: "Second private desk draft: a small light and an empty night corridor.",
    17: "Older standby-envelope label intended for the upcoming watch.",
    18: "Older commissioning-envelope label, a boat and the first crossing.",
    0: "Final keeper-envelope desk margin: people making room after a late watch, the sea outside, night nearly finished, and voices around a table.",
}

def tokens(s):
    return re.findall(r"[a-z0-9]+", s.lower())

def norm(s):
    return " ".join(tokens(s))

def caption(t):
    return t.split(":", 1)[-1].strip()

def load():
    raw = (ROOT / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CREW_SHA
    records = re.findall(r"N(\d\d) / ([^\n]+)\n([^\n]+)", raw.decode())
    notes = {int(n): (a.split()[0], t) for n, a, t in records}
    assert list(notes) == list(range(1, 25))
    assert {k for k, (a, _) in notes.items() if a == "Emily"} == {2,6,10,13,17,18,20,23}
    mails = {i: (ROOT / f"resources/evidence/mail/{i:02d}.eml").read_text().split("\n\n", 1)[-1] for i in (11,20)}
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    assert nonce.hex().upper() == "5F933DA6A1BD03C32DA5CBC25344F497"
    assert target.hex() == "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
    assert hmac.digest(nonce,norm(caption(notes[2][1])).encode(),"sha256")[:16].hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
    return notes,mails,nonce,target

def decoys(notes, held):
    n = len(tokens(caption(notes[held][1])))
    rows = [(i,caption(t)) for i,(a,t) in notes.items() if i != held]
    rows.sort(key=lambda x:(abs(len(tokens(x[1]))-n),x[0]))
    return rows[:11]

def masked_source(notes,mails,held,purpose,excluded=frozenset()):
    forbidden = set(tokens(caption(notes[held][1]))) if held else set()
    def mask(s):
        return re.sub(r"\b[A-Za-z0-9]+\b",lambda m:"[withheld]" if m.group().lower() in forbidden else m.group(),s)
    parts = [f"N{i:02d} by {a}: {t}" for i,(a,t) in notes.items() if i != held and i not in excluded]
    parts += [f"MAIL{i:02d}: {s}" for i,s in mails.items()]
    role = ROLE[held] if purpose else "A historical H-17 crew note."
    prompt=("Predict one missing original caption by Emily using the incomplete record.\n"
            +"Historical excerpts:\n"+"\n".join(parts)+"\nTarget purpose: "+role
            +"\nRespond with one full line only:")
    prompt = mask(prompt)
    assert not (set(tokens(prompt)) & forbidden)
    return prompt

def chat(tokenizer,prompt):
    return tokenizer.apply_chat_template([
        {"role":"system","content":"Return one complete crew caption only."},
        {"role":"user","content":prompt},
    ],tokenize=False,add_generation_prompt=True)

def logprob(model,tokenizer,torch,prefix,sentence):
    ids=tokenizer(prefix,return_tensors="pt",add_special_tokens=False).input_ids
    suffix=tokenizer(" "+sentence,return_tensors="pt",add_special_tokens=False).input_ids
    all_ids=torch.cat((ids,suffix),dim=1)
    with torch.inference_mode():
        logits=model(all_ids).logits[0,ids.shape[1]-1:-1]
    score=torch.nn.functional.log_softmax(logits,dim=-1).gather(1,suffix[0].unsqueeze(1)).sum()
    return round((score/suffix.shape[1]).item(),6)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--case",type=int,choices=CASES,required=True)
    parser.add_argument("--smoke",action="store_true")
    args=parser.parse_args()
    notes,mails,nonce,target=load()
    case=args.case
    excluded=frozenset(i for i,_ in decoys(notes,case)) if case else frozenset()
    for mode in (True,False):
        prompt=masked_source(notes,mails,case,mode,excluded)
        print("MASKED_SOURCE",json.dumps({"case":case,"purpose":mode,"chars":len(prompt),"decoys":sorted(excluded),"sha256":hashlib.sha256(prompt.encode()).hexdigest()}),flush=True)
    if args.smoke:
        return
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    torch.set_num_threads(4)
    tokenizer=AutoTokenizer.from_pretrained(MODEL)
    model=AutoModelForCausalLM.from_pretrained(MODEL,torch_dtype=torch.float32,low_cpu_mem_usage=True)
    model.eval()
    if case==0:
        prompt=chat(tokenizer,masked_source(notes,mails,0,True))
        inputs=tokenizer(prompt,return_tensors="pt",add_special_tokens=False)
        seen=set()
        hits=[]
        for j in range(16):
            torch.manual_seed(20261106+j)
            with torch.inference_mode():
                out=model.generate(**inputs,max_new_tokens=42,do_sample=j>0,
                    temperature=0.8 if j else None,top_p=0.9 if j else None,
                    pad_token_id=tokenizer.eos_token_id)
            text=tokenizer.decode(out[0,inputs.input_ids.shape[1]:],skip_special_tokens=True).splitlines()[0]
            phrase=norm(text)
            if not phrase or phrase in seen:
                continue
            seen.add(phrase)
            component=hmac.digest(nonce,phrase.encode(),"sha256")[:16]
            good=hashlib.sha256(component).digest()==target
            if good:
                hits.append({"phrase":phrase,"component":component.hex().upper()})
            print("ORIGINAL_TARGET",json.dumps({"rank":j+1,"phrase":phrase,"hit":good}),flush=True)
        print("FINAL",json.dumps({"unique":len(seen),"hits":hits}),flush=True)
        return
    target_sentence=norm(caption(notes[case][1]))
    candidates=[(case,target_sentence)]+[(i,norm(s)) for i,s in decoys(notes,case)]
    result={"case":case}
    for name,flag in (("purpose",True),("generic",False)):
        prompt=chat(tokenizer,masked_source(notes,mails,case,flag,excluded))
        scores=[{"note":i,"score":logprob(model,tokenizer,torch,prompt,s)} for i,s in candidates]
        scores.sort(key=lambda item:-item["score"])
        rank=next(i for i,v in enumerate(scores,1) if v["note"]==case)
        result[name]={"rank":rank,"out_of":len(scores),"scores":scores}
    print("BLIND_RANK",json.dumps(result),flush=True)

if __name__=="__main__":
    main()
