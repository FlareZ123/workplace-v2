"""Short-evidence author-voice synthesis with exact full-text controls and copy veto.

Contrast to prior full-archive cloze: admit only intact author examples, omit long
context snippets, and reject exact source copying. The frozen candidate producer is
read-only with respect to original records and checks the original K08 acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
from pathlib import Path

from filelock import FileLock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k08_author_15b_fourholdout_sft as source

MODEL = "Qwen/Qwen2.5-3B-Instruct"
REVISION = "aa8e72537993ba99e69dfaafa59ed015b17504d1"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
SEED = 20261104 + 9117
CHOICES = ("n02", "n06", "keeper", "zoey_keeper")

SCENES = {
    "n02": "A first crew-board draft for a warm, ordinary handover between watches.",
    "n06": "A second personal desk draft at the end of a long night.",
    "keeper": "The final handwritten keeper-envelope margin after a long watch. Outside is the sea, inside the crew have made room for one another at the table as morning approaches.",
    "zoey_keeper": "The final handwritten keeper-envelope margin after a long watch. Outside is the sea, inside the crew have made room for one another at the table as morning approaches.",
}

PROMPTS = (
    "Write one newly composed handwritten caption in this author's style. Use 7 to 18 words, concrete objects, and the author's ordinary voice. Do not quote, restate or discuss the examples. Give the caption alone.",
    "Supply a new single-sentence handwritten inscription for the requested purpose. Keep it specific, plainspoken and understated. Never copy an example or refer to notes, captions, envelopes or drafts in the answer.",
)

def load(case: str):
    resources = ROOT / "resources"
    raw = (resources / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == NOTES_SHA
    notes = source.get_notes(raw.decode("utf-8"))
    route = json.loads((resources / "evidence/recovery-routing.json").read_text("utf-8"))
    acceptance = json.loads((resources / "acceptance.json").read_text("utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    wanted = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    assert hmac.digest(nonce, source.norm(notes[2][1]).encode(), "sha256")[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    held = {"n02": 2, "n06": 6}.get(case)
    voice = "Zoey" if case == "zoey_keeper" else "Emily"
    author_examples = (
        [3, 9, 16, 21] if voice == "Zoey"
        else [n for n in (2, 6, 13, 17, 18) if n != held]
    )
    exemplars = [notes[i][1] for i in author_examples]
    joined = "\n".join(f"- {s}" for s in exemplars)
    context = (
        f"Handwritten sentences previously authored by {voice}:\n{joined}\n\n"
        f"Writing assignment: {SCENES[case]}\n\n"
    )
    if held:
        assert source.norm(notes[held][1]) not in source.norm(context), f"leaked N{held:02d}"
    prompts = [context + p for p in PROMPTS]
    truth = source.norm(notes[held][1]) if held else None
    sources = {source.norm(v[1]) for v in notes.values()}
    return prompts, nonce, wanted, truth, sources, voice

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=CHOICES, required=True)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    prompts, nonce, wanted, truth, originals, voice = load(args.case)
    print("SCENE_MASK_AND_REDUCER_PASS", args.case, voice, [len(p) for p in prompts], flush=True)
    if args.smoke:
        return
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, revision=REVISION, torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    model.eval()
    out = Path(__file__).with_name(f"k08_shortvoice_{args.case}.jsonl")
    rows = []
    unique = set()
    novel = set()
    exact_ranks = []
    hits = []
    for prompt_id, prompt in enumerate(prompts):
        conversation = tokenizer.apply_chat_template(
            [{"role":"system", "content":"You write complete short handwritten sentences. Return a caption alone, no commentary."},
             {"role":"user", "content": prompt}],
            tokenize=False, add_generation_prompt=True,
        )
        inputs = tokenizer(conversation, return_tensors="pt", add_special_tokens=False)
        for batch in range(3):
            seed = SEED + 10000 * CHOICES.index(args.case) + 100 * prompt_id + batch
            torch.manual_seed(seed)
            with torch.inference_mode():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=48,
                    do_sample=True,
                    temperature=1.07,
                    top_p=0.94,
                    repetition_penalty=1.07,
                    num_return_sequences=4,
                    pad_token_id=tokenizer.eos_token_id,
                )
            for sample_id, tokens in enumerate(outputs):
                generated = tokenizer.decode(
                    tokens[inputs.input_ids.shape[1]:],
                    skip_special_tokens=True,
                )
                caption = source.one_sentence(generated)
                normalized = source.norm(caption)
                if not normalized:
                    continue
                component = hmac.digest(nonce, normalized.encode(), "sha256")[:16]
                hit = hashlib.sha256(component).digest() == wanted
                exact = (normalized == truth) if truth is not None else None
                if exact:
                    exact_ranks.append(len(rows) + 1)
                if hit:
                    hits.append({"caption":caption, "component":component.hex().upper()})
                copied = normalized in originals
                novel_case = not copied and normalized not in unique and not any(
                    key in normalized for key in (
                        "desk copy", "desk margin line was", "the phrase should",
                        "the caption is", "the envelope label",
                    )
                )
                unique.add(normalized)
                if novel_case:
                    novel.add(normalized)
                row = {
                    "case": args.case, "voice":voice, "prompt_id":prompt_id,
                    "batch":batch, "sample":sample_id, "seed":seed,
                    "rank":len(rows)+1,"caption":caption,
                    "normalized":normalized,"copies_source":copied,
                    "novel":novel_case,"control_exact":exact,
                    "original_k08_hit":hit,
                }
                rows.append(row)
                print("CANDIDATE", json.dumps(row, ensure_ascii=False), flush=True)
            with FileLock(str(out)+".lock"):
                tmp=out.with_suffix(out.suffix+".tmp")
                tmp.write_text("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in rows),encoding="utf-8")
                os.replace(tmp,out)
            print("BATCH_COMPLETED",args.case,prompt_id,batch,len(rows),flush=True)
    print("FINAL_CASE_RESULT",json.dumps({
        "case":args.case,"voice":voice,"model":MODEL,"revision":REVISION,
        "source_sha":NOTES_SHA,"count":len(rows),"unique":len(unique),
        "novel_unique":len(novel),"source_copies":sum(x["copies_source"] for x in rows),
        "exact_control_ranks":exact_ranks,"original_k08_hits":hits,
        "artifact":str(out),
    }),flush=True)

if __name__ == "__main__":
    main()
