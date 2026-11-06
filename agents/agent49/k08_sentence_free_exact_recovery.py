"""Sentence-free, source-conditioned K08 exact-recovery pilot.

All surviving source records are represented as per-record unordered token
inventories with frequencies and provenance. Exact captions and quoted copies
are masked by the original missingness-matched source logic. The model must
reconstruct held-out whole captions from independent lexical evidence without
copying complete surviving sentences.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent8"))
import k08_independent_lexical_ab_3b_sft as base

MODEL_REPO = "Qwen/Qwen2.5-3B-Instruct-GGUF"
MODEL_FILE = "qwen2.5-3b-instruct-q4_k_m.gguf"
MODEL_REVISION = "7dabda4d13d513e3e842b20f0d435c732f172cbe"
CONTROL_CASES = (2, 6, 17, 18)
TARGET_CASE = 0
TARGET_UNIQUE = 64
MAX_BATCHES = 8
BATCH_LINES = 10
MAX_TOKENS = 512

K08_CUE_TOKENS = (
    "people", "making", "room", "each", "other", "after", "long", "watch",
    "water", "outside", "night", "almost", "finished", "sea", "end",
    "voices", "table",
)


def configure_base(notes: dict) -> None:
    base.ROLE = {
        2: "First draft for the crew board.",
        6: "Second desk draft.",
        17: "Standby-envelope label.",
        18: "Commissioning-envelope label.",
    }
    base.WRONG_ROLE = {
        2: base.ROLE[6],
        6: base.ROLE[2],
        17: base.ROLE[18],
        18: base.ROLE[17],
    }
    for case, role in base.ROLE.items():
        content_vocab = set(base.tokens(notes[case]["caption"])) - base.STOPWORDS
        assert not (set(base.tokens(role)) & content_vocab)
    for case, role in base.WRONG_ROLE.items():
        content_vocab = set(base.tokens(notes[case]["caption"])) - base.STOPWORDS
        assert not (set(base.tokens(role)) & content_vocab)

    log_path = base.ROOT / "resources/evidence/crew/galley-and-stores.log"
    galley_log = log_path.read_text("utf-8").strip()
    assert hashlib.sha256(log_path.read_bytes()).hexdigest() == (
        "23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46"
    )
    original_source_records = base.source_records

    def source_records_with_galley_log(notes, mails, held, excluded, phrases):
        records = original_source_records(notes, mails, held, excluded, phrases)
        clean, manifest = base.sanitize_record(
            "GALLEY_LOG", "GALLEY_LOG | " + galley_log, phrases
        )
        records.append(("GALLEY_LOG", clean, manifest))
        return records

    base.source_records = source_records_with_galley_log


def inventory_record(source_id: str, clean: str, manifest: dict,
                     notes: dict, mails: dict) -> str:
    if source_id.startswith("N"):
        number = int(source_id[1:])
        row = notes[number]
        content = clean.split("|", 2)[-1]
        metadata = (
            f"author={row['author']}; heading={' '.join(row['heading'])}; "
            f"role={base.ROLE.get(number, 'crew note')}"
        )
    elif source_id.startswith("MAIL"):
        number = int(source_id[4:])
        row = mails[number]
        content = clean.split("|", 4)[-1]
        metadata = (
            f"sender={row['sender']}; date={row['date']}; "
            f"subject={row['subject']}"
        )
    elif source_id == "GALLEY_LOG":
        content = clean.split("|", 1)[-1]
        metadata = "record_type=galley_and_stores_log"
    elif source_id == "K08_ROUTE":
        content = clean
        metadata = "record_type=K08_route_metadata"
    elif source_id == "CUSTODIAN":
        content = clean
        metadata = "record_type=records_custodian_note"
    else:
        content = clean
        metadata = "record_type=other"

    tokens = base.tokens(content)
    counts = Counter(tokens)
    inventory = ", ".join(f"{word}:{counts[word]}" for word in sorted(counts))
    return (
        f"{source_id} | {metadata} | token_count={len(tokens)} | "
        f"masked_exact={len(manifest['exact_phrase_replacements'])} | "
        f"masked_quotes={len(manifest['quoted_span_replacements'])} | "
        f"UNORDERED_WORD_INVENTORY: {inventory}"
    )


def build_records(case: int, notes: dict, mails: dict):
    if case in CONTROL_CASES:
        _, manifest, excluded_rows = base.make_prompt(
            notes, mails, case, "B", "proper"
        )
        excluded = {number for number, _ in excluded_rows}
        phrase_rows = [(f"N{case:02d}", notes[case]["caption"])] + [
            (f"N{number:02d}", phrase) for number, phrase in excluded_rows
        ]
        records = base.source_records(
            notes, mails, case, excluded, phrase_rows
        )
    else:
        phrase_rows = [
            ("N17", notes[17]["caption"]),
            ("N18", notes[18]["caption"]),
        ]
        records = base.source_records(notes, mails, 0, set(), phrase_rows)
        manifest = {
            "case": 0,
            "purpose": "final K08 keeper-envelope caption",
            "source_records": len(records) + 2,
            "withheld_phrases": ["N17", "N18"],
        }
        route_path = base.ROOT / "resources/evidence/recovery-routing.json"
        route = json.loads(route_path.read_text("utf-8"))["K08"]
        safe_route = {
            key: value for key, value in route.items()
            if not any(term in key.lower() for term in ("nonce", "sha", "digest", "hash"))
        }
        route_text = json.dumps(safe_route, ensure_ascii=False, sort_keys=True)
        clean, route_manifest = base.sanitize_record(
            "K08_ROUTE", route_text, phrase_rows
        )
        records.append(("K08_ROUTE", clean, route_manifest))

        custodian_path = base.ROOT / "resources/evidence/records-custodian.txt"
        custodian_text = custodian_path.read_text("utf-8")
        clean, custodian_manifest = base.sanitize_record(
            "CUSTODIAN", custodian_text, phrase_rows
        )
        records.append(("CUSTODIAN", clean, custodian_manifest))

    inventory = [
        inventory_record(source_id, clean, item, notes, mails)
        for source_id, clean, item in records
    ]
    return inventory, manifest, phrase_rows


def build_prompt(case: int, notes: dict, mails: dict):
    inventory, manifest, phrase_rows = build_records(case, notes, mails)
    if case in CONTROL_CASES:
        role = base.ROLE[case]
        target_meta = (
            f"target_record=N{case:02d}; author={notes[case]['author']}; "
            f"target_role={role}; excluded_decoys={manifest['excluded_decoys']}"
        )
        header = (
            "TASK: reconstruct one missing historical whole-caption inscription. "
            f"{target_meta}. The target note and eleven length-matched decoy notes "
            "are absent. Independent words remain in other original records. "
        )
    else:
        header = (
            "TASK: reconstruct the final K08 keeper-envelope personal desk caption. "
            "target_author=Emily; target_role_tokens=[personal, keeper, desk, phrase, "
            "late, watch, spirit, not, technical, incident, title, not, official, "
            "slogan]. K08_SEMANTIC_CUE_TOKENS_UNORDERED=["
            + ", ".join(K08_CUE_TOKENS)
            + "]. "
        )

    prompt = (
        header
        + "SOURCE_REPRESENTATION: every record below is reduced to an unordered "
        "per-record word inventory with frequencies and provenance. Original word "
        "order and complete sentence spans have been destroyed. Do not reproduce "
        "any surviving source sentence; use independent lexical evidence, author "
        "identity, chronology, and record role to reconstruct the missing original. "
        "Write natural English, not a word list or an official procedure.\n"
        "SOURCE_RECORD_INVENTORIES:\n"
        + "\n".join(inventory)
        + "\nOUTPUT: exactly ten distinct complete caption candidates, each 3–24 "
        "words, numbered 1. through 10., one per line, no explanation or commentary."
    )

    normalized_prompt = base.norm(prompt)
    for number, row in notes.items():
        phrase = base.norm(row["caption"])
        assert phrase not in normalized_prompt, (case, f"N{number:02d} sentence survived")
    for _, phrase in phrase_rows:
        assert base.norm(phrase) not in normalized_prompt, (case, "withheld phrase leaked")
    if case == 0:
        prompt_tokens = set(base.tokens(prompt))
        assert set(K08_CUE_TOKENS).issubset(prompt_tokens)
    else:
        assert manifest["independent_word_overlap_total"] > 0, manifest
    return prompt, manifest


def parse_candidates(text: str) -> list[str]:
    numbered = []
    fallback = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"^(?:\d{1,2}[.):]|[-*•])\s*(.+)$", line)
        if match:
            line = match.group(1).strip()
            destination = numbered
        else:
            if re.match(r"^(?:here are|candidates?:|options?:)", line, re.I):
                continue
            destination = fallback
        phrase = base.norm(line.strip().strip('"').strip("“”"))
        count = len(phrase.split())
        if 2 <= count <= 32:
            destination.append(phrase)
    return numbered if numbered else fallback


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
    parser.add_argument("--output", type=Path, default=Path("k08-sentence-free-candidates.jsonl"))
    args = parser.parse_args()

    notes, mails, nonce, target = base.load_sources()
    configure_base(notes)
    prompts = {}
    manifests = {}
    for case in (*CONTROL_CASES, TARGET_CASE):
        prompt, manifest = build_prompt(case, notes, mails)
        prompts[case] = prompt
        manifests[case] = manifest
        print("SOURCE_MANIFEST", json.dumps({
            **manifest,
            "case": case,
            "source_mode": "sentence-free-per-record-unordered-token-inventory",
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "prompt_chars": len(prompt),
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
    model_sha = hashlib.sha256()
    with model_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            model_sha.update(chunk)
    model_sha_hex = model_sha.hexdigest()
    print("MODEL_SOURCE", json.dumps({
        "repo": MODEL_REPO,
        "file": MODEL_FILE,
        "revision": MODEL_REVISION,
        "sha256": model_sha_hex,
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
    summaries = {}
    for case in CONTROL_CASES:
        prompt = prompts[case]
        prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        expected = base.norm(notes[case]["caption"])
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
                        "You reconstruct historical captions from unordered lexical "
                        "evidence. Return only the requested numbered candidates."
                    )},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.85,
                top_p=0.95,
                top_k=50,
                max_tokens=MAX_TOKENS,
                repeat_penalty=1.05,
                seed=seed,
            )
            content = response["choices"][0]["message"]["content"] or ""
            parsed = parse_candidates(content)
            batch_rows = []
            for rank, phrase in enumerate(parsed, 1):
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
                    "exact_control_match": phrase == expected,
                    "source_mode": "sentence-free-per-record-unordered-token-inventory",
                    "model_sha256": model_sha_hex,
                    "prompt_sha256": prompt_sha,
                }
                if row["exact_control_match"]:
                    hits.append(row)
                batch_rows.append(row)
                all_rows.append(row)
            atomic_write_jsonl(args.output, all_rows)
            print("BATCH_PROGRESS", json.dumps({
                "case": case,
                "batch": batch + 1,
                "seed": seed,
                "parsed_lines": len(parsed),
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
            "exact_control_rank": hits[0]["unique_rank"] if hits else None,
            "model_sha256": model_sha_hex,
            "prompt_sha256": prompt_sha,
            "source_manifest": manifests[case],
        }
        summaries[case] = summary
        print("CASE_SUMMARY", json.dumps(summary, ensure_ascii=False), flush=True)

    positive_hits = {
        case for case in (2, 6)
        if summaries[case]["exact_hit_count"] > 0
    }
    if positive_hits == {2, 6}:
        case = TARGET_CASE
        prompt = prompts[case]
        prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        seen: set[str] = set()
        hits = []
        attempts = 0
        for batch in range(args.max_batches):
            if len(seen) >= args.target_unique:
                break
            attempts += 1
            seed = 20261106 + batch
            response = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": (
                        "You reconstruct a personal keeper-envelope caption from "
                        "unordered historical lexical evidence. Return only the "
                        "requested numbered candidates."
                    )},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.85,
                top_p=0.95,
                top_k=50,
                max_tokens=MAX_TOKENS,
                repeat_penalty=1.05,
                seed=seed,
            )
            content = response["choices"][0]["message"]["content"] or ""
            parsed = parse_candidates(content)
            batch_rows = []
            for rank, phrase in enumerate(parsed, 1):
                if phrase in seen:
                    continue
                seen.add(phrase)
                component = base.candidate_component(nonce, phrase)
                row = {
                    "case": 0,
                    "batch": batch,
                    "seed": seed,
                    "rank_in_batch": rank,
                    "unique_rank": len(seen),
                    "phrase": phrase,
                    "word_count": len(phrase.split()),
                    "component_hex": component.hex().upper(),
                    "target_match": hashlib.sha256(component).hexdigest() == target,
                    "source_mode": "sentence-free-per-record-unordered-token-inventory",
                    "model_sha256": model_sha_hex,
                    "prompt_sha256": prompt_sha,
                }
                if row["target_match"]:
                    hits.append(row)
                batch_rows.append(row)
                all_rows.append(row)
            atomic_write_jsonl(args.output, all_rows)
            print("BATCH_PROGRESS", json.dumps({
                "case": 0,
                "batch": batch + 1,
                "seed": seed,
                "parsed_lines": len(parsed),
                "new_unique": len(batch_rows),
                "unique_total": len(seen),
                "target_hits": len(hits),
                "response_chars": len(content),
            }), flush=True)
            for row in batch_rows:
                print("CANDIDATE", json.dumps(row, ensure_ascii=False), flush=True)
        summaries[0] = {
            "case": 0,
            "unique_candidates": len(seen),
            "target_unique": args.target_unique,
            "batches": attempts,
            "target_hit_count": len(hits),
            "target_hit_ranks": [row["unique_rank"] for row in hits],
            "model_sha256": model_sha_hex,
            "prompt_sha256": prompt_sha,
            "source_manifest": manifests[0],
        }
        print("CASE_SUMMARY", json.dumps(summaries[0], ensure_ascii=False), flush=True)
    else:
        print("FINAL_SKIPPED", json.dumps({
            "reason": "both positive whole-caption controls N02 and N06 did not recover exactly",
            "positive_control_hits": sorted(positive_hits),
            "final_target_candidates_generated": 0,
        }), flush=True)

    print("FINAL_SUMMARY", json.dumps(summaries, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
