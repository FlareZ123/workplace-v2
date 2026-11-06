"""Sharded whole-caption beam rehearsal and direct K08 target contact.

Four deterministic 3B beam candidates per held-out authentic caption (N02/N06/
N17/N18) measure exact recovery under realistic whole-line/quote missingness.
The same frozen beam editor generates four complete N23 keeper candidates,
which are checked against the original HMAC16 and SHA256 commitments.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "agents" / "agent8"))

import k08_independent_lexical_ab_3b_sft_v3 as v3

base = v3.base
MODEL = "Qwen/Qwen2.5-3B-Instruct"
CASES = (0, 2, 6, 17, 18)
BEAMS = 4
MAX_NEW_TOKENS = 32


def build_prompt(case: int, notes: dict, mails: dict) -> tuple[str, dict]:
    if case == 0:
        prompt = base.final_prompt(notes, mails)
        manifest = {
            "case": 0,
            "source_records": 45,
            "purpose": "final keeper-envelope caption",
        }
    else:
        prompt, manifest, _ = base.make_prompt(notes, mails, case, "B", "proper")
    assert prompt
    if case == 0:
        assert base.norm(notes[17]["caption"]) not in base.norm(prompt)
        assert base.norm(notes[18]["caption"]) not in base.norm(prompt)
    else:
        assert base.norm(notes[case]["caption"]) not in base.norm(prompt)
    return prompt, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int, choices=CASES, required=True)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    notes, mails, nonce, target = base.load_sources()
    prompt, manifest = build_prompt(args.case, notes, mails)
    prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    print("SOURCE_MANIFEST", json.dumps({
        **manifest,
        "model": MODEL,
        "prompt_sha256": prompt_sha,
        "prompt_chars": len(prompt),
        "beams": BEAMS,
        "max_new_tokens": MAX_NEW_TOKENS,
        "withheld_phrase_absent": True,
    }), flush=True)
    if args.smoke:
        return

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float32, low_cpu_mem_usage=True
    )
    model.eval()

    prefix = base.chat_prefix(tokenizer, prompt)
    inputs = tokenizer(prefix, return_tensors="pt", add_special_tokens=False)
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            num_beams=BEAMS,
            num_return_sequences=BEAMS,
            early_stopping=True,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            return_dict_in_generate=True,
        )

    expected = base.norm(notes[args.case]["caption"]) if args.case else None
    candidates = []
    seen = set()
    for rank, sequence in enumerate(output.sequences, 1):
        raw = tokenizer.decode(
            sequence[inputs.input_ids.shape[1]:], skip_special_tokens=True
        )
        phrase = base.norm(raw.splitlines()[0].strip().strip('"')) if raw.strip() else ""
        duplicate = phrase in seen
        seen.add(phrase)
        row = {
            "rank": rank,
            "phrase": phrase,
            "unique": not duplicate,
            "word_count": len(phrase.split()),
        }
        if args.case == 0:
            component = base.candidate_component(nonce, phrase) if phrase else b""
            row["component"] = component.hex().upper()
            row["target_match"] = bool(phrase) and hashlib.sha256(component).hexdigest() == target
        else:
            row["exact_control_match"] = phrase == expected
        candidates.append(row)

    result = {
        "case": args.case,
        "model": MODEL,
        "decoding": {
            "method": "deterministic beam search",
            "num_beams": BEAMS,
            "num_return_sequences": BEAMS,
            "max_new_tokens": MAX_NEW_TOKENS,
            "early_stopping": True,
        },
        "prompt_sha256": prompt_sha,
        "candidate_count": len(candidates),
        "unique_normalized_candidates": len(seen),
        "exact_control_rank": next(
            (row["rank"] for row in candidates if row.get("exact_control_match")),
            None,
        ) if args.case else None,
        "target_hits": [row for row in candidates if row.get("target_match")],
        "candidates": candidates,
    }
    print("EXACT_RECOVERY_RESULT", json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
