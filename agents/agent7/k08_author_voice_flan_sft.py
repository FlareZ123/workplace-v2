#!/usr/bin/env python3
"""Pretrained author-voice generator for exact K08 commitment search.

This is an exploratory candidate generator. It preserves the original K08
normalizer/HMAC/SHA acceptance path and measures exact output coverage on four
known Emily lines before interpreting target output quality.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import random
import re
import tempfile
from pathlib import Path

import fcntl
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "agent7-k08-author-model"
MODEL = "google/flan-t5-small"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
N02_KAT = "BF889359B0303F2B2B2FD96AE841210B"

CONTROLS = {
    "N02": (
        "a good watch leaves the room ready for the next pair of hands",
        "Write one short plain-spoken crew-board sentence in Emily's voice. "
        "Meaning: after a good watch, leave the room ready for the next pair of hands. "
        "Output only the sentence."
    ),
    "N06": (
        "the little lamp stays on until the corridor has gone quiet",
        "Write one short plain-spoken desk sentence in Emily's voice. "
        "Meaning: the little lamp remains on until the corridor is quiet. "
        "Output only the sentence."
    ),
    "N17": (
        "leave the light on for the next watch",
        "Write one very short standby envelope label in Emily's voice. "
        "Meaning: keep the light on for the next watch. Output only the label."
    ),
    "N18": (
        "back before the first boat",
        "Write one very short commissioning envelope label in Emily's voice. "
        "Meaning: return before the first boat. Output only the label."
    ),
}

TARGET_PROMPTS = [
    "Write the final keeper-envelope line in Emily's plain crew-room voice. "
    "It is about late crew making room for one another after a long watch, "
    "with the water outside, the night almost finished, and voices at the table. "
    "It should sound warm and natural, like a photograph caption after the last cup. "
    "Do not use the old standby labels. Output only one complete sentence.",

    "Emily needs one concise final photograph-caption line for the keeper envelope. "
    "Hold together the sea outside, the end of the night, the voices at the table, "
    "and people making room for each other after a long watch. Plain spoken, unstaged, "
    "crew-room language. Output only the final line.",

    "Create one natural final margin inscription in Emily's voice for the late crew: "
    "people make room for one another after a long watch; water is outside; the night "
    "is nearly over; there are voices around the table. The photograph was revisited "
    "after the last cup. Avoid quarterly-report language. Output only the inscription.",

    "One sentence only. Emily's final keeper caption should feel like us: a long watch "
    "ending, the sea outside, familiar voices at the table, and room made for one another. "
    "Quiet, warm, ordinary language, suitable for a margin copied onto an envelope."
]

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

def generate(model, tokenizer, prompt: str, count: int, seed: int) -> list[str]:
    results: list[str] = []
    # Deterministic high-probability beams first.
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.inference_mode():
        beam_n = min(64, count)
        beam = model.generate(
            **inputs,
            max_new_tokens=32,
            num_beams=beam_n,
            num_return_sequences=beam_n,
            early_stopping=True,
            length_penalty=0.8,
        )
    results.extend(tokenizer.batch_decode(beam, skip_special_tokens=True))

    remaining = count - beam_n
    batch = 32
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    # generate() has no generator kwarg across all supported Transformers versions;
    # seed torch globally before each prompt for deterministic sampling.
    torch.manual_seed(seed)
    while remaining > 0:
        n = min(batch, remaining)
        with torch.inference_mode():
            sampled = model.generate(
                **inputs,
                max_new_tokens=32,
                do_sample=True,
                temperature=0.85,
                top_p=0.96,
                top_k=80,
                num_return_sequences=n,
                repetition_penalty=1.04,
            )
        results.extend(tokenizer.batch_decode(sampled, skip_special_tokens=True))
        remaining -= n
    return results

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--control-count", type=int, default=512)
    ap.add_argument("--target-count", type=int, default=2048)
    args = ap.parse_args()
    if args.control_count < 64 or args.target_count < 64:
        ap.error("counts must be >=64")

    # Validate original reducer with the published known answer.
    n02 = component(CONTROLS["N02"][0]).hex().upper()
    if n02 != N02_KAT:
        raise RuntimeError(f"N02 KAT mismatch: {n02}")

    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    if acceptance["slot_sha256"]["K08"] != TARGET:
        raise RuntimeError("K08 target changed")
    if bytes.fromhex(routing["K08"]["desk_nonce"]) != NONCE:
        raise RuntimeError("K08 nonce changed")

    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)
    model.eval()
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))

    report: dict[str, object] = {
        "model": MODEL,
        "controls": {},
        "target_prompts": [],
        "unique_target_candidates": 0,
        "acceptance_hits": [],
    }
    seen_target: dict[str, str] = {}

    for idx, (name, (expected, prompt)) in enumerate(CONTROLS.items()):
        outputs = generate(model, tokenizer, prompt, args.control_count, 76119 + idx)
        normalized = [normalize(x) for x in outputs]
        unique = list(dict.fromkeys(x for x in normalized if x))
        rank = unique.index(expected) + 1 if expected in unique else None
        report["controls"][name] = {
            "expected": expected,
            "generated": len(outputs),
            "unique": len(unique),
            "exact_rank": rank,
            "top20": unique[:20],
        }
        print(
            "CONTROL "
            + json.dumps({"name": name, "unique": len(unique), "exact_rank": rank}),
            flush=True,
        )

    for idx, prompt in enumerate(TARGET_PROMPTS):
        outputs = generate(model, tokenizer, prompt, args.target_count, 88001 + idx)
        unique = list(dict.fromkeys(normalize(x) for x in outputs if normalize(x)))
        report["target_prompts"].append({
            "prompt_index": idx,
            "generated": len(outputs),
            "unique": len(unique),
            "top50": unique[:50],
        })
        for phrase in unique:
            seen_target.setdefault(phrase, f"prompt{idx}")
            if accepted(phrase):
                hit = {
                    "phrase": phrase,
                    "source_prompt": idx,
                    "component_hex": component(phrase).hex().upper(),
                }
                report["acceptance_hits"].append(hit)
                print("K08_HIT " + json.dumps(hit), flush=True)

    report["unique_target_candidates"] = len(seen_target)
    atomic_json(OUT / "summary.json", report)
    print(
        "AUTHOR_MODEL_COMPLETE "
        + json.dumps({
            "controls_exact": sum(
                1 for value in report["controls"].values() if value["exact_rank"] is not None
            ),
            "unique_target_candidates": len(seen_target),
            "hits": len(report["acceptance_hits"]),
        }),
        flush=True,
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
