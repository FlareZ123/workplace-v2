#!/usr/bin/env python3
"""Second-stage K08 author-voice search with Qwen2.5-0.5B-Instruct.

The experiment is deliberately gated by leave-one-out exact reconstruction of
four known Emily lines. Target candidates are checked only through the original
normalization, HMAC and SHA-256 commitment.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import tempfile
from pathlib import Path

import fcntl
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "agent7-k08-qwen"
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
N02_KAT = "BF889359B0303F2B2B2FD96AE841210B"

KNOWN = {
    "N02": "a good watch leaves the room ready for the next pair of hands",
    "N06": "the little lamp stays on until the corridor has gone quiet",
    "N17": "leave the light on for the next watch",
    "N18": "back before the first boat",
}
STYLE = [
    "I still like the photograph after the last cup. The desk copy should sound like us, not like a quarterly report.",
    "The mugs were still by the window after the late watch and somebody had left the little lamp on.",
    "I want the keeper line to hold the sea, the end of the night and the voices at the table without making any of it sound staged.",
]
MEANINGS = {
    "N02": "after a good watch, leave the room ready for the next pair of hands",
    "N06": "the little lamp remains on until the corridor is quiet",
    "N17": "keep the light on for the next watch",
    "N18": "return before the first boat",
}
TARGET_BRIEF = (
    "The final keeper-envelope caption is about late crew making room for one another "
    "after a long watch. It should hold the water or sea outside, the night almost "
    "finished, and familiar voices at the table. Emily kept returning to the photograph "
    "after the last cup. The line should sound like the crew, warm and ordinary, and "
    "must not reuse the old standby or commissioning labels as the final wording."
)

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())

def component(text: str) -> bytes:
    return hmac.new(NONCE, normalize(text).encode("ascii"), hashlib.sha256).digest()[:16]

def accepted(text: str) -> bool:
    return hashlib.sha256(component(text)).hexdigest() == TARGET

def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(value, stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    lock_path.unlink(missing_ok=True)

def make_control_prompt(name: str) -> str:
    other = [line for key, line in KNOWN.items() if key != name]
    examples = "\n".join(f"- {line}" for line in other + STYLE)
    return (
        "You are reconstructing a short handwritten line by Emily from an archive. "
        "Use the examples only to learn her plain, compact wording.\n"
        f"Other known Emily lines and notes:\n{examples}\n"
        f"Missing line meaning: {MEANINGS[name]}.\n"
        "Write the single most natural original line. Output only the line, no quotes or explanation."
    )

def make_target_prompt(variant: int) -> str:
    examples = "\n".join(f"- {line}" for line in list(KNOWN.values()) + STYLE)
    endings = [
        "Favor a compact photograph caption.",
        "Favor a handwritten margin line that is easy to remember.",
        "Favor ordinary crew-room language rather than literary language.",
        "Favor a line Emily could copy directly onto an envelope.",
    ]
    return (
        "You are reconstructing Emily's final handwritten keeper-envelope caption from surviving drafts.\n"
        f"Known Emily voice examples:\n{examples}\n"
        f"Final-line brief: {TARGET_BRIEF}\n"
        f"{endings[variant]} Output only one complete candidate line, no quotes or explanation."
    )

def generate(model, tokenizer, prompt: str, count: int, seed: int) -> list[str]:
    messages = [
        {"role": "system", "content": "Return only the requested short archival line."},
        {"role": "user", "content": prompt},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt")
    input_len = inputs["input_ids"].shape[1]
    results: list[str] = []

    # Small beam slice.
    beams = min(8, count)
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=32,
            num_beams=beams,
            num_return_sequences=beams,
            early_stopping=True,
            length_penalty=0.8,
            pad_token_id=tokenizer.eos_token_id,
        )
    results.extend(tokenizer.batch_decode(output[:, input_len:], skip_special_tokens=True))

    torch.manual_seed(seed)
    remaining = count - beams
    while remaining:
        n = min(8, remaining)
        with torch.inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=32,
                do_sample=True,
                temperature=0.9,
                top_p=0.97,
                top_k=80,
                repetition_penalty=1.03,
                num_return_sequences=n,
                pad_token_id=tokenizer.eos_token_id,
            )
        results.extend(tokenizer.batch_decode(output[:, input_len:], skip_special_tokens=True))
        remaining -= n
    return results

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--control-count", type=int, default=128)
    ap.add_argument("--target-count", type=int, default=256)
    args = ap.parse_args()
    if args.control_count < 8 or args.target_count < 8:
        ap.error("counts must be at least 8")

    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    if acceptance["slot_sha256"]["K08"] != TARGET:
        raise RuntimeError("K08 target changed")
    if bytes.fromhex(routing["K08"]["desk_nonce"]) != NONCE:
        raise RuntimeError("K08 nonce changed")
    if component(KNOWN["N02"]).hex().upper() != N02_KAT:
        raise RuntimeError("N02 reducer known-answer control failed")

    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32)
    model.eval()
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))

    report: dict[str, object] = {
        "model": MODEL,
        "controls": {},
        "target_prompts": [],
        "acceptance_hits": [],
    }
    target_seen: dict[str, int] = {}

    for idx, name in enumerate(KNOWN):
        outputs = generate(model, tokenizer, make_control_prompt(name), args.control_count, 91000 + idx)
        unique = list(dict.fromkeys(normalize(x) for x in outputs if normalize(x)))
        expected = KNOWN[name]
        rank = unique.index(expected) + 1 if expected in unique else None
        report["controls"][name] = {
            "expected": expected,
            "generated": len(outputs),
            "unique": len(unique),
            "exact_rank": rank,
            "top20": unique[:20],
        }
        print("CONTROL " + json.dumps({"name": name, "unique": len(unique), "exact_rank": rank}), flush=True)

    for variant in range(4):
        outputs = generate(model, tokenizer, make_target_prompt(variant), args.target_count, 92000 + variant)
        unique = list(dict.fromkeys(normalize(x) for x in outputs if normalize(x)))
        report["target_prompts"].append({
            "variant": variant,
            "generated": len(outputs),
            "unique": len(unique),
            "top50": unique[:50],
        })
        for phrase in unique:
            target_seen.setdefault(phrase, variant)
            if accepted(phrase):
                hit = {
                    "phrase": phrase,
                    "variant": variant,
                    "component_hex": component(phrase).hex().upper(),
                }
                report["acceptance_hits"].append(hit)
                print("K08_HIT " + json.dumps(hit), flush=True)

    report["unique_target_candidates"] = len(target_seen)
    atomic_json(OUT / "summary.json", report)
    print("QWEN_AUTHOR_COMPLETE " + json.dumps({
        "controls_exact": sum(1 for v in report["controls"].values() if v["exact_rank"] is not None),
        "unique_target_candidates": len(target_seen),
        "hits": len(report["acceptance_hits"]),
    }), flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
