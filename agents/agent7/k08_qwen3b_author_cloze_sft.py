"""Source-masked Emily author-voice cloze, complete-caption Qwen2.5-3B CPU test.

Five separately isolated cases: four genuine authored controls and final K08.
Never supplies a hidden caption to model prompts. Original records are read-only.
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

MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
MODEL_REVISION = "aa8e725"
SEED = 20261104
NOTES_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
CASES = (2, 6, 17, 18, 0)
SCENES = {
    2: "First handwritten crew-board draft about the handover from an outgoing watch to the incoming crew.",
    6: "Second personal desk draft, in the setting of a dim night corridor and a small window lamp.",
    17: "Brief standby-envelope label for the next crew on watch, associated with a lamp at the window.",
    18: "Brief commissioning-envelope label associated with the crew boat and the first crossing.",
    0: "Final keeper-envelope desk-margin line, after a long watch: sea outside, night almost over, crew voices at the table and making room for each other.",
}
NOTE_SELECTION = (1, 2, 6, 8, 9, 10, 11, 13, 17, 18, 19, 20, 23)
MAIL_SELECTION = (11, 12, 14, 20)
INSTRUCTIONS = (
    "Reconstruct the missing sentence as an archival cloze. Prefer Emily's concrete, ordinary diction and natural sentence length. Output only one complete inscription.",
    "Imagine Emily revising the surviving handwritten phrases into this purpose. Keep her cadence and specific physical objects. Output only the new sentence.",
    "Predict the single exact-sounding caption she would write after rereading these source notes. Avoid formal slogans, explanations and lists. Output one sentence only.",
)

def material_for(notes: dict, mails: dict, held: int) -> str:
    rows = []
    for idx in NOTE_SELECTION:
        if idx != held:
            author, phrase = notes[idx]
            rows.append(f"N{idx:02d} / {author}: {phrase}")
    for idx in MAIL_SELECTION:
        mail = mails[idx].split("\n\n", 1)[-1]
        if held:
            target = notes[held][1].rstrip(".!?")
            mail = re.sub(re.escape(target) + r"[.!?]?", "[withheld inscription]", mail, flags=re.I)
        rows.append(f"MAIL-{idx:02d}: {mail}")
    text = "\n\n".join(rows)
    if held:
        assert source.norm(notes[held][1]) not in source.norm(text), f"source leak in N{held:02d}"
    return text

def load(case: int) -> tuple[list[str], bytes, bytes, str | None]:
    resources = ROOT / "resources"
    original = (resources / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(original).hexdigest() == NOTES_SHA256
    notes = source.get_notes(original.decode("utf-8"))
    assert len(notes) == 24
    mails = {i: (resources / f"evidence/mail/{i:02d}.eml").read_text("utf-8") for i in MAIL_SELECTION}
    material = material_for(notes, mails, case)
    route = json.loads((resources / "evidence/recovery-routing.json").read_text("utf-8"))
    acceptance = json.loads((resources / "acceptance.json").read_text("utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    wanted = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    assert nonce.hex().upper() == "5F933DA6A1BD03C32DA5CBC25344F497"
    assert wanted.hex() == "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
    assert hmac.digest(nonce, source.norm(notes[2][1]).encode(), "sha256")[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    truth = source.norm(notes[case][1]) if case else None
    prompt_prefix = (
        "Historical personal crew-board and desk-caption extracts from the same incident:\n"
        + material
        + "\n\nThe desired missing record is by Emily. Purpose: " + SCENES[case] + "\n\n"
    )
    prompts = [prompt_prefix + instruction for instruction in INSTRUCTIONS]
    return prompts, nonce, wanted, truth

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int, choices=CASES, required=True)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    prompts, nonce, wanted, truth = load(args.case)
    print("ORIGINAL_SOURCE_MASK_AND_REDUCER_PASS", args.case,
          "prompt_chars", [len(x) for x in prompts],
          "known_heldout", truth if args.smoke else bool(truth), flush=True)
    if args.smoke:
        return

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from huggingface_hub import model_info

    torch.set_num_threads(4)
    print("MODEL_REQUEST", MODEL_ID, MODEL_REVISION, flush=True)
    revision_sha = model_info(MODEL_ID, revision=MODEL_REVISION).sha
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    model.eval()
    print("MODEL_READY", revision_sha, flush=True)
    output = Path(__file__).with_name(f"k08_qwen3b_case{args.case:02d}.jsonl")
    rows = []
    uniq = set()
    exact_ranks = []
    matches = []
    for prompt_id, prompt in enumerate(prompts):
        chat = tokenizer.apply_chat_template(
            [
                {"role": "system", "content": "Reconstruct one missing historical handwritten caption. Return only the completed sentence."},
                {"role": "user", "content": prompt},
            ],
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = tokenizer(chat, return_tensors="pt", add_special_tokens=False)
        seed = SEED + 1000 * args.case + prompt_id
        for sampling in (False, True):
            torch.manual_seed(seed + (100000 if sampling else 0))
            with torch.inference_mode():
                generated = model.generate(
                    **inputs,
                    max_new_tokens=52,
                    do_sample=sampling,
                    temperature=0.83 if sampling else None,
                    top_p=0.91 if sampling else None,
                    num_return_sequences=4 if sampling else 1,
                    pad_token_id=tokenizer.eos_token_id,
                )
            for tokens in generated:
                text = tokenizer.decode(
                    tokens[inputs.input_ids.shape[1]:],
                    skip_special_tokens=True,
                )
                caption = source.one_sentence(text)
                normalized = source.norm(caption)
                if not normalized:
                    continue
                component = hmac.digest(nonce, normalized.encode(), "sha256")[:16]
                original_hit = hashlib.sha256(component).digest() == wanted
                exact = (normalized == truth) if truth is not None else None
                if original_hit:
                    matches.append({"caption": caption, "component": component.hex().upper()})
                if exact:
                    exact_ranks.append(len(rows) + 1)
                uniq.add(normalized)
                row = {
                    "case": args.case, "model": MODEL_ID, "revision": revision_sha,
                    "seed": seed, "prompt_id": prompt_id, "sampling": sampling,
                    "rank": len(rows) + 1, "caption": caption,
                    "normalized": normalized, "heldout_exact": exact,
                    "original_k08_hit": original_hit,
                }
                rows.append(row)
                print("EMITTED", json.dumps(row, ensure_ascii=False), flush=True)
        print("PROMPT_COMPLETED", args.case, prompt_id, len(rows), flush=True)
        with FileLock(str(output) + ".lock"):
            temp = output.with_suffix(output.suffix + ".tmp")
            temp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
            os.replace(temp, output)
    print("FINAL_CASE_RESULT", json.dumps({
        "case": args.case, "model": MODEL_ID, "revision": revision_sha,
        "source_sha": NOTES_SHA256, "count": len(rows), "unique": len(uniq),
        "control_exact_ranks": exact_ranks, "original_k08_hits": matches,
        "output": str(output),
    }), flush=True)

if __name__ == "__main__":
    main()
