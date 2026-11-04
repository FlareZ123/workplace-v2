"""Short-form elliptical keeper inscription search, source-masked label controls.

Different mechanism from complete-sentence reconstruction: targets historically
short envelope inscriptions as compact titles/fragments. Original sources,
HMAC, slot commitment and verifier remain untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from pathlib import Path

from filelock import FileLock

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent49"))
import k08_author_15b_fourholdout_sft as prior

MODEL="Qwen/Qwen2.5-3B-Instruct"
REVISION="aa8e72537993ba99e69dfaafa59ed015b17504d1"
NOTES_SHA="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
SCENE={
    17:"a standby recovery envelope from one crew watch to the next",
    18:"a commissioning envelope from the early crossing and boat crew",
    0:"a personal keeper envelope at the end of a long watch: sea outside, dawn close, welcoming voices around the crew-room table",
}
TASKS=(
    "Write a new memorable handwritten label, 4 to 9 words. A fragment or compact image is preferable. Write only the words on the envelope, without quotes.",
    "Compress the scene into a new short personal caption of at most ten words, with the quiet voice of the examples. Avoid complete explanations, avoid repeating prior labels.",
)

def setup(case):
    resources=ROOT/"resources"
    raw=(resources/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==NOTES_SHA
    notes=prior.get_notes(raw.decode())
    targets=json.loads((resources/"acceptance.json").read_text())
    nonce=bytes.fromhex(json.loads((resources/"evidence/recovery-routing.json").read_text())["K08"]["desk_nonce"])
    target=bytes.fromhex(targets["slot_sha256"]["K08"])
    assert hmac.digest(nonce,prior.norm(notes[2][1]).encode(),"sha256")[:16].hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
    examples=[i for i in (2,6,13,17,18) if i!=case]
    material="\n".join("• "+notes[i][1] for i in examples)
    prefix=f"Prior handwritten lines by Emily:\n{material}\n\nWrite a separate label for this purpose: {SCENE[case]}.\n"
    if case:
        assert prior.norm(notes[case][1]) not in prior.norm(prefix)
    return [prefix+"\n"+v for v in TASKS],nonce,target,prior.norm(notes[case][1]) if case else None,{prior.norm(v[1]) for v in notes.values()}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--case",required=True,type=int,choices=tuple(SCENE))
    ap.add_argument("--smoke",action="store_true")
    args=ap.parse_args()
    prompts,nonce,target,truth,originals=setup(args.case)
    print("ORIGINAL_SOURCE_SHORT_LABEL_MASK_PASS",args.case,[len(x) for x in prompts],flush=True)
    if args.smoke:return
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    torch.set_num_threads(4)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REVISION)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REVISION,torch_dtype=torch.float32,low_cpu_mem_usage=True)
    model.eval()
    out=Path(__file__).with_name(f"k08_elliptical3b_case{args.case:02d}.jsonl")
    allrows=[];unique=set();novel=set();hits=[];exact=[]
    for pidx,prompt in enumerate(prompts):
        chat=tok.apply_chat_template(
            [{"role":"system","content":"You write a short and distinctive handwritten caption. Output only the caption words."},
             {"role":"user","content":prompt}],
            tokenize=False,add_generation_prompt=True)
        ins=tok(chat,return_tensors="pt",add_special_tokens=False)
        for batch in range(3):
            seed=20261104+40000+args.case*100+pidx*1000+batch
            torch.manual_seed(seed)
            with torch.inference_mode():
                outputs=model.generate(**ins,max_new_tokens=36,do_sample=True,temperature=1.06,top_p=0.91,
                                       repetition_penalty=1.08,num_return_sequences=4,
                                       pad_token_id=tok.eos_token_id)
            for sample,tokens in enumerate(outputs):
                caption=prior.one_sentence(tok.decode(tokens[ins.input_ids.shape[1]:],skip_special_tokens=True))
                normalized=prior.norm(caption)
                if not normalized:continue
                component=hmac.digest(nonce,normalized.encode(),"sha256")[:16]
                hit=hashlib.sha256(component).digest()==target
                is_exact=(normalized==truth) if truth is not None else None
                copied=normalized in originals
                first=normalized not in unique
                unique.add(normalized)
                if first and not copied:novel.add(normalized)
                if hit:hits.append({"caption":caption,"K08":component.hex().upper()})
                if is_exact:exact.append(len(allrows)+1)
                row={"case":args.case,"prompt":pidx,"batch":batch,"sample":sample,
                     "rank":len(allrows)+1,"text":caption,"normalized":normalized,
                     "copied_source":copied,"control_exact":is_exact,"original_k08_hit":hit}
                allrows.append(row)
                print("CANDIDATE",json.dumps(row,ensure_ascii=False),flush=True)
            with FileLock(str(out)+".lock"):
                tmp=out.with_suffix(".jsonl.tmp")
                tmp.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in allrows),encoding="utf-8")
                os.replace(tmp,out)
            print("BATCH_COMPLETED",args.case,pidx,batch,len(allrows),flush=True)
    print("FINAL_CASE_RESULT",json.dumps({"case":args.case,"model":MODEL,"model_commit":REVISION,
          "total":len(allrows),"unique":len(unique),"novel_unique":len(novel),
          "source_copies":sum(x["copied_source"] for x in allrows),
          "control_exact_ranks":exact,"K08_hits":hits}),flush=True)

if __name__=="__main__":main()
