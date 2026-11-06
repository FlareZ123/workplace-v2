"""Quantized Qwen/llama.cpp K08 exact-recovery rehearsal.

One Q4_K_M model instance generates batches of ten complete candidates for
N02/N06/N17/N18 held-out controls and the final N23 keeper phrase. Every
unique normalized candidate is checked through the original commitment path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "agents" / "agent8"))
import k08_independent_lexical_ab_3b_sft_v3 as v3

base = v3.base
MODEL_REPO = "Qwen/Qwen2.5-3B-Instruct-GGUF"
MODEL_FILE = "qwen2.5-3b-instruct-q4_k_m.gguf"
MODEL_REVISION = "main"
CASES = (2, 6, 17, 18, 0)
TARGET_UNIQUE = 100
MAX_BATCHES = 12
BATCH_LINES = 10
MAX_TOKENS = 512


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_prompt(case: int, notes: dict, mails: dict) -> tuple[str, dict]:
    if case == 0:
        prompt = base.final_prompt(notes, mails)
        manifest = {
            "case": 0,
            "source_records": 45,
            "purpose": "final keeper-envelope caption",
        }
        prompt += (
            "\n\nA full contiguous-span check of the exported UTF-8 evidence "
            "found no exact K08 commitment match for any source phrase of "
            "1–32 words. Treat a light edit or new keeper line as the leading "
            "possibility. The final wording must still fit the custodian's "
            "personal late-watch description and the original evidence.\n"
        )
    else:
        prompt, manifest, _ = base.make_prompt(notes, mails, case, "B", "proper")
    prompt += (
        f"\n\nOverride any earlier single-line output instruction for this "
        f"batch: produce exactly {BATCH_LINES} distinct, complete caption "
        "candidates. Put one candidate on each numbered line (1. through 10.). "
        "No heading, explanation, or commentary. Each candidate must be a "
        "standalone phrase grounded in the supplied historical evidence.\n"
    )
    return prompt, manifest


def parse_candidates(text: str) -> list[str]:
    parsed = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"^(?:\d{1,2}[.)]|[-*•])\s*(.+)$", line)
        if match:
            line = match.group(1).strip()
        elif re.match(r"^(?:here are|candidates?:|options?:)", line, re.I):
            continue
        phrase = base.norm(line.strip().strip('"').strip("“”"))
        count = len(phrase.split())
        if 2 <= count <= 32:
            parsed.append(phrase)
    return parsed


def atomic_write_jsonl(path: Path, rows: list[dict]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    payload = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    temp.write_text(payload, encoding="utf-8")
    os.replace(temp, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--target-unique", type=int, default=TARGET_UNIQUE)
    parser.add_argument("--max-batches", type=int, default=MAX_BATCHES)
    parser.add_argument("--output", type=Path, default=Path("k08-llamacpp-exact-candidates.jsonl"))
    args = parser.parse_args()

    notes, mails, nonce, target = base.load_sources()
    prompts = {}
    for case in CASES:
        prompt, manifest = build_prompt(case, notes, mails)
        if case == 0:
            assert base.norm(notes[17]["caption"]) not in base.norm(prompt)
            assert base.norm(notes[18]["caption"]) not in base.norm(prompt)
        else:
            assert base.norm(notes[case]["caption"]) not in base.norm(prompt)
        prompts[case] = prompt
        print("SOURCE_MANIFEST", json.dumps({
            **manifest,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "prompt_chars": len(prompt),
            "withheld_phrase_absent": True,
        }), flush=True)
    if args.smoke:
        return

    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama

    model_path = Path(hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILE,
        revision=MODEL_REVISION,
    ))
    model_sha = sha256_file(model_path)
    print("MODEL_SOURCE", json.dumps({
        "repo": MODEL_REPO,
        "file": MODEL_FILE,
        "revision": MODEL_REVISION,
        "sha256": model_sha,
        "quantization": "Q4_K_M",
    }), flush=True)

    llm = Llama(
        model_path=str(model_path),
        n_ctx=8192,
        n_threads=4,
        n_batch=512,
        chat_format="chatml",
        verbose=False,
    )

    all_rows: list[dict] = []
    summaries = []
    for case in CASES:
        prompt = prompts[case]
        prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        expected = base.norm(notes[case]["caption"]) if case else None
        seen: set[str] = set()
        hits = []
        attempts = 0

        for batch in range(args.max_batches):
            if len(seen) >= args.target_unique:
                break
            attempts += 1
            seed = 20261106 + case * 100000 + batch
            response = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": (
                        "You are reconstructing a historical personal desk caption. "
                        "Return only the requested numbered caption candidates."
                    )},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.85,
                top_p=0.95,
                top_k=50,
                max_tokens=MAX_TOKENS,
                repeat_penalty=1.05,
                seed=seed,
                stop=["\n\n"],
            )
            content = response["choices"][0]["message"]["content"] or ""
            batch_rows = []
            for rank, phrase in enumerate(parse_candidates(content), 1):
                if phrase in seen:
                    continue
                seen.add(phrase)
                row = {
                    "case": case,
                    "batch": batch,
                    "seed": seed,
                    "rank_in_batch": rank,
                    "unique_rank": len(seen),
                    "phrase": phrase,
                    "word_count": len(phrase.split()),
                    "model_sha256": model_sha,
                    "prompt_sha256": prompt_sha,
                }
                if case == 0:
                    component = base.candidate_component(nonce, phrase)
                    row["component_hex"] = component.hex().upper()
                    row["target_match"] = hashlib.sha256(component).hexdigest() == target
                else:
                    row["exact_control_match"] = phrase == expected
                if row.get("target_match") or row.get("exact_control_match"):
                    hits.append(row)
                batch_rows.append(row)
                all_rows.append(row)

            atomic_write_jsonl(args.output, all_rows)
            print("BATCH_PROGRESS", json.dumps({
                "case": case,
                "batch": batch + 1,
                "seed": seed,
                "parsed_lines": len(parse_candidates(content)),
                "new_unique": len(batch_rows),
                "unique_total": len(seen),
                "exact_hits": len(hits),
                "response_chars": len(content),
            }), flush=True)
            for row in batch_rows:
                print("CANDIDATE", json.dumps(row, ensure_ascii=False), flush=True)

        summary = {
            "case": case,
            "unique_candidates": len(seen),
            "target_unique": args.target_unique,
            "batches": attempts,
            "exact_hit_count": len(hits),
            "exact_control_rank": hits[0]["unique_rank"] if hits and case else None,
            "target_hits": hits if case == 0 else [],
            "model_repo": MODEL_REPO,
            "model_file": MODEL_FILE,
            "model_sha256": model_sha,
            "prompt_sha256": prompt_sha,
        }
        summaries.append(summary)
        print("CASE_SUMMARY", json.dumps(summary, ensure_ascii=False), flush=True)

    print("FINAL_SUMMARY", json.dumps(summaries, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
