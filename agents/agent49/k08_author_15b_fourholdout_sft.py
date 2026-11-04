"""K08 source-masked four-caption calibration and final keeper candidate experiment."""
from __future__ import annotations
import argparse, hashlib, hmac, json, os, re
from pathlib import Path
from filelock import FileLock

ROOT = Path(__file__).resolve().parents[2] / "resources"
OUT = Path(__file__).with_name("k08_author_15b_candidates.jsonl")
MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
SEED = 20261104
SHA_NOTES = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
PURPOSE = {
 2: "first crew-board draft, a short personal watch handover caption",
 6: "second personal desk draft, after a long night",
 17: "old standby recovery envelope, a very short memorable label",
 18: "old commissioning recovery envelope, a very short memorable label",
 0: "final keeper recovery envelope, personal line about people making room at a table after a night watch, the sea outside, morning approaching",
}

def norm(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())

def get_notes(raw: str) -> dict[int, tuple[str, str]]:
    lines = raw.splitlines()
    notes = {}
    for i, line in enumerate(lines[:-1]):
        m = re.fullmatch(r"N(\d{2}) / (.+)", line)
        if m:
            notes[int(m.group(1))] = (m.group(2).split()[0], lines[i+1].split(": ",1)[-1].strip())
    assert len(notes)==24
    return notes

def one_sentence(generated: str) -> str:
    line = generated.strip().splitlines()[0].strip() if generated.strip() else ""
    line = re.sub(r"^(?:Caption|Answer|Final|Draft)\s*:\s*", "", line, flags=re.I)
    line = re.sub(r"^(?:[-*]|\d+[.)])\s*", "", line).strip(" \t\"'‘’“”")
    return re.split(r"(?<=[.!?])\s+", line)[0].strip(" \t\"'‘’“”")

def context(notes: dict, mails: list[str], held: int, swap: bool) -> tuple[str, str]:
    author = "Zoey" if swap else "Emily"
    rows = [
        f"N{i:02d} / {name}: {value}"
        for i,(name,value) in sorted(notes.items())
        if i != held and (name != "Emily" or not swap)
        and (name not in {"Zoey","Jason"} or swap)
    ]
    blocks = []
    for m in mails:
        body = m.split("\n\n",1)[1] if "\n\n" in m else m
        for old in (notes[17][1],notes[18][1]):
            body = re.sub(re.escape(old.rstrip(".!?")), "[older envelope label redacted]", body, flags=re.I)
        blocks.append(body)
    material = "\n".join(rows) + "\n\nCorrespondence:\n" + "\n".join(blocks)
    if held:
        assert norm(notes[held][1]) not in norm(material), f"target leak N{held:02d}"
    return material,author

def prompts(held: int, author: str, material: str) -> list[str]:
    purpose = PURPOSE[held]
    return [
      f"Surviving archival extracts:\n{material}\n\nPredict one likely complete handwritten sentence by {author} for this purpose: {purpose}. Output only the sentence without quotes.",
      f"Surviving archival extracts:\n{material}\n\nComplete a missing short crew caption in {author}'s understated concrete style with everyday objects and one sentence. Purpose: {purpose}. Only the caption.",
    ]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke",action="store_true")
    args = parser.parse_args()
    raw = (ROOT/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA_NOTES
    notes = get_notes(raw.decode())
    mails = [(ROOT/f"evidence/mail/{i:02d}.eml").read_text(encoding="utf-8") for i in range(1,21)]
    route = json.loads((ROOT/"evidence/recovery-routing.json").read_text())
    target = json.loads((ROOT/"acceptance.json").read_text())["slot_sha256"]["K08"]
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    def comp(s: str) -> bytes:
        return hmac.digest(nonce,norm(s).encode(),"sha256")[:16]
    assert comp(notes[2][1]).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    cases = [(held,swap) for held in (2,6,17,18) for swap in (False,True)] + [(0,False)]
    contexts = {(held,swap):context(notes,mails,held,swap) for held,swap in cases}
    if args.smoke:
        for (held,swap),(material,author) in contexts.items():
            print("MASK_OK",held,swap,author,len(material))
        print("SOURCE_AND_REDUCER_SMOKE_PASS")
        return
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL,torch_dtype=torch.float32,low_cpu_mem_usage=True)
    model.eval()
    records = []
    stats = {}
    for case_id,(held,swap) in enumerate(cases):
        material,author = contexts[(held,swap)]
        name = f"N{held:02d}_"+("swap" if swap else "author") if held else "K08_final"
        unique = set()
        exact = []
        hits = []
        count = 0
        for pi, text in enumerate(prompts(held,author,material)):
            messages = [
              {"role":"system","content":"Restore historical handwritten crew captions. Reply with exactly one complete sentence."},
              {"role":"user","content":text},
            ]
            templated = tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
            inputs = tokenizer(templated,return_tensors="pt",add_special_tokens=False)
            seed = SEED + 10000*case_id + pi
            torch.manual_seed(seed)
            with torch.inference_mode():
                outputs = model.generate(**inputs,max_new_tokens=48,do_sample=True,temperature=0.9,
                    top_p=0.93,num_return_sequences=8 if held==0 else 5,pad_token_id=tokenizer.eos_token_id)
            for si, tokens in enumerate(outputs):
                caption = one_sentence(tokenizer.decode(tokens[inputs.input_ids.shape[1]:],skip_special_tokens=True))
                normalized = norm(caption)
                if not normalized: continue
                count += 1
                unique.add(normalized)
                is_exact = held != 0 and normalized == norm(notes[held][1])
                original_hit = hashlib.sha256(comp(normalized)).hexdigest() == target
                if is_exact: exact.append([pi,si])
                if original_hit: hits.append({"caption":caption,"component":comp(normalized).hex().upper()})
                records.append({"case":name,"prompt":pi,"sample":si,"seed":seed,"caption":caption,
                                "normalized":normalized,"heldout_exact":is_exact if held else None,"K08_hit":original_hit})
        stats[name] = {"total":count,"unique":len(unique),"exact":exact,"K08_hits":hits}
        print("CASE_RESULT",json.dumps({"case":name,**stats[name]}),flush=True)
        with FileLock(str(OUT)+".lock"):
            temp = OUT.with_suffix(".jsonl.tmp")
            temp.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in records),encoding="utf-8")
            os.replace(temp,OUT)
    print("FINAL_RESULT",json.dumps({"model":MODEL,"seed":SEED,"notes_sha":SHA_NOTES,"stats":stats}),flush=True)

if __name__ == "__main__":
    main()
