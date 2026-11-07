"""Paired K08 historical-caption A/B: strict lexical denial vs phrase-only holdout.

Reuses Agent9's exact source loader, authentic decoy selector, Qwen scorer,
purpose descriptions and scoring rule. Arm A is the quote-clean, all-target-word
masked baseline. Arm B removes only complete target/decoy phrase occurrences
from source excerpts, retaining independently occurring target words.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent9"))

import k08_blind_author_rank_sft as ranker
import k08_blind_author_rank_quote_clean as quote_clean  # patches ranker.masked_source

ARM_A_SOURCE = ranker.masked_source
CASES = (2, 6, 17, 18)
SWAP = {2: 6, 6: 2, 17: 18, 18: 17}
GENERIC_ROLE = "A historical H-17 crew note."
OUT = ROOT / "k08-ab-out"


def phrase_regex(phrase: str) -> re.Pattern[str]:
    words = ranker.tokens(phrase)
    if not words:
        raise ValueError("empty phrase")
    middle = r"[\W_]+".join(re.escape(word) for word in words)
    return re.compile(r"(?<![A-Za-z0-9])" + middle + r"(?![A-Za-z0-9])", re.IGNORECASE)


def phrase_sequence_present(text: str, phrase: str) -> bool:
    source_words = ranker.tokens(text)
    phrase_words = ranker.tokens(phrase)
    if not phrase_words:
        return False
    width = len(phrase_words)
    return any(source_words[i:i + width] == phrase_words for i in range(len(source_words) - width + 1))


def remove_phrases(
    text: str,
    source_id: str,
    phrase_specs: list[tuple[int, str, str]],
    manifest: list[dict[str, object]],
) -> str:
    for phrase_id, phrase, phrase_kind in phrase_specs:
        pattern = phrase_regex(phrase)

        def replace(match: re.Match[str]) -> str:
            manifest.append({
                "source_id": source_id,
                "withheld_note_id": phrase_id,
                "matched_text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "reason": "complete target quotation" if phrase_kind == "target" else "complete decoy quotation",
            })
            return "[withheld complete phrase]"

        text = pattern.sub(replace, text)
    return text


def prepare_sources(
    notes: dict[int, tuple[str, str]],
    mails: dict[int, str],
    held: int,
    excluded: frozenset[int],
) -> tuple[dict[int, tuple[str, str]], dict[int, str], dict[str, object]]:
    decoy_specs = [(i, ranker.caption(notes[i][1]), "decoy") for i in sorted(excluded)]
    target_spec = [(held, ranker.caption(notes[held][1]), "target")]
    phrase_specs = target_spec + decoy_specs
    phrase_manifest: list[dict[str, object]] = []

    source_notes = copy.deepcopy(notes)
    source_mails = dict(mails)
    for note_id, (author, text) in notes.items():
        if note_id == held or note_id in excluded:
            continue
        source_notes[note_id] = (
            author,
            remove_phrases(text, f"N{note_id:02d}", phrase_specs, phrase_manifest),
        )
    for mail_id, text in mails.items():
        source_mails[mail_id] = remove_phrases(
            text, f"MAIL{mail_id:02d}", phrase_specs, phrase_manifest
        )

    target_words = sorted(set(ranker.tokens(ranker.caption(notes[held][1]))))
    retained: dict[str, dict[str, int]] = {}
    arm_a_masks: dict[str, dict[str, int]] = {}
    independent_spans: dict[str, list[dict[str, object]]] = {}
    for source_id, text in (
        [(f"N{i:02d}", t) for i, (author, t) in source_notes.items()
         if i != held and i not in excluded]
        + [(f"MAIL{i:02d}", t) for i, t in source_mails.items()]
    ):
        spans = []
        for match in re.finditer(r"[A-Za-z0-9]+", text):
            word = match.group(0).lower()
            if word in target_words:
                spans.append({
                    "word": word,
                    "start": match.start(),
                    "end": match.end(),
                    "classification": "independent occurrence after complete-phrase removal",
                })
        if spans:
            independent_spans[source_id] = spans
            counts: dict[str, int] = {}
            for span in spans:
                word = str(span["word"])
                counts[word] = counts.get(word, 0) + 1
            retained[source_id] = counts
            arm_a_masks[source_id] = dict(counts)

    manifest = {
        "case": held,
        "target_phrase": ranker.caption(notes[held][1]),
        "target_normalized": ranker.norm(ranker.caption(notes[held][1])),
        "target_words": target_words,
        "decoy_note_ids": sorted(excluded),
        "decoy_phrases": {str(i): ranker.caption(notes[i][1]) for i in sorted(excluded)},
        "phrase_removals": phrase_manifest,
        "arm_a_word_mask_counts": arm_a_masks,
        "arm_a_independent_word_mask_spans": independent_spans,
        "arm_b_independent_word_occurrences_retained": retained,
        "arm_b_independent_word_occurrence_spans_retained": independent_spans,
        "word_span_offset_basis": "phrase-cleaned source excerpt; target and decoy full phrases already replaced",
    }
    return source_notes, source_mails, manifest


def arm_a_prompt(
    notes: dict[int, tuple[str, str]],
    mails: dict[int, str],
    held: int,
    excluded: frozenset[int],
    condition: str,
) -> str:
    if condition == "generic":
        return ARM_A_SOURCE(notes, mails, held, False, excluded)
    original_role = ranker.ROLE[held]
    try:
        if condition == "swapped":
            ranker.ROLE[held] = ranker.ROLE[SWAP[held]]
        return ARM_A_SOURCE(notes, mails, held, True, excluded)
    finally:
        ranker.ROLE[held] = original_role


def arm_b_prompt(
    notes: dict[int, tuple[str, str]],
    mails: dict[int, str],
    held: int,
    excluded: frozenset[int],
    condition: str,
) -> str:
    parts = [
        f"N{i:02d} by {author}: {text}"
        for i, (author, text) in notes.items()
        if i != held and i not in excluded
    ]
    parts += [f"MAIL{i:02d}: {text}" for i, text in mails.items()]
    if condition == "generic":
        role = GENERIC_ROLE
    elif condition == "swapped":
        role = ranker.ROLE[SWAP[held]]
    else:
        role = ranker.ROLE[held]
    prompt = (
        "Predict one missing original caption by Emily using the incomplete record.\n"
        "Historical excerpts:\n" + "\n".join(parts)
        + "\nTarget purpose: " + role
        + "\nRespond with one full line only:"
    )
    return prompt


def build_case(
    notes: dict[int, tuple[str, str]],
    mails: dict[int, str],
    held: int,
) -> tuple[dict[str, object], dict[str, str], list[tuple[int, str]]]:
    excluded = frozenset(i for i, _ in ranker.decoys(notes, held))
    source_notes, source_mails, manifest = prepare_sources(notes, mails, held, excluded)
    candidates = [(held, ranker.norm(ranker.caption(notes[held][1])))] + [
        (i, ranker.norm(text)) for i, text in ranker.decoys(notes, held)
    ]
    assert len(candidates) == 12
    assert len({i for i, _ in candidates}) == 12

    prompts: dict[str, str] = {}
    prompt_hashes: dict[str, str] = {}
    for arm in ("A", "B"):
        for condition in ("purpose", "generic", "swapped"):
            key = f"{arm}_{condition}"
            if arm == "A":
                prompt = arm_a_prompt(source_notes, source_mails, held, excluded, condition)
            else:
                prompt = arm_b_prompt(source_notes, source_mails, held, excluded, condition)
            target_phrase = ranker.caption(notes[held][1])
            for note_id in excluded:
                decoy_phrase = ranker.caption(notes[note_id][1])
                assert not phrase_sequence_present(prompt, decoy_phrase), (held, arm, condition, note_id)
            assert not phrase_sequence_present(prompt, target_phrase), (held, arm, condition, "target")
            if arm == "A":
                forbidden = set(ranker.tokens(target_phrase))
                assert not (set(ranker.tokens(prompt)) & forbidden), (held, condition, "strict mask")
            prompts[key] = prompt
            prompt_hashes[key] = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    manifest["prompt_sha256"] = prompt_hashes
    manifest["arm_b_retains_any_target_word"] = {
        word: sum(src.get(word, 0) for src in manifest["arm_b_independent_word_occurrences_retained"].values())
        for word in manifest["target_words"]
    }
    return manifest, prompts, candidates


def validate_case_maps(
    run_cases: tuple[int, ...],
    manifests: dict[str, dict[str, object]],
    prompt_sets: dict[int, dict[str, str]],
    candidate_sets: dict[int, list[tuple[int, str]]],
) -> tuple[int, ...]:
    """Validate the exact requested holdouts before smoke or model scoring."""
    requested = tuple(run_cases)
    expected = set(requested)
    assert len(requested) == len(expected), ("duplicate requested holdout", requested)
    assert set(manifests) == {str(held) for held in requested}
    assert set(prompt_sets) == expected
    assert set(candidate_sets) == expected

    expected_prompt_keys = {
        "A_purpose", "A_generic", "A_swapped",
        "B_purpose", "B_generic", "B_swapped",
    }
    for held in requested:
        manifest = manifests[str(held)]
        assert manifest["case"] == held
        prompts = prompt_sets[held]
        assert set(prompts) == expected_prompt_keys

        target_phrase = str(manifest["target_phrase"])
        target_words = set(ranker.tokens(target_phrase))
        decoy_phrases = [str(value) for value in manifest["decoy_phrases"].values()]
        for prompt_key, prompt in prompts.items():
            assert not phrase_sequence_present(prompt, target_phrase), (
                held, prompt_key, "target phrase leaked into prompt"
            )
            for decoy_phrase in decoy_phrases:
                assert not phrase_sequence_present(prompt, decoy_phrase), (
                    held, prompt_key, "decoy phrase leaked into prompt"
                )
            if prompt_key.startswith("A_"):
                assert not (set(ranker.tokens(prompt)) & target_words), (
                    held, prompt_key, "strict Arm A target-word mask failed"
                )

        candidates = candidate_sets[held]
        assert len(candidates) == 12
        assert candidates[0] == (held, str(manifest["target_normalized"]))
        assert len({note_id for note_id, _ in candidates}) == 12
        assert {note_id for note_id, _ in candidates[1:]} == set(
            int(note_id) for note_id in manifest["decoy_note_ids"]
        )

    return requested


def rank_scores(model, tokenizer, torch, prefix: str, candidates: list[tuple[int, str]]) -> dict[str, object]:
    scores = [
        {"note": note_id, "text": text,
         "score": ranker.logprob(model, tokenizer, torch, prefix, text)}
        for note_id, text in candidates
    ]
    scores.sort(key=lambda item: -item["score"])
    true = next(item for item in scores if item["note"] == candidates[0][0])
    decoy_top = max(item["score"] for item in scores if item["note"] != candidates[0][0])
    return {
        "rank": next(i for i, item in enumerate(scores, 1) if item["note"] == candidates[0][0]),
        "out_of": len(scores),
        "target_score": true["score"],
        "best_decoy_score": decoy_top,
        "target_minus_best_decoy": round(true["score"] - decoy_top, 6),
        "scores": scores,
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--case", type=int, choices=CASES)
    args = parser.parse_args()
    run_cases = (args.case,) if args.case is not None else CASES

    notes, mails, nonce, target = ranker.load()
    assert nonce.hex().upper() == "5F933DA6A1BD03C32DA5CBC25344F497"
    assert target.hex() == "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"

    manifests: dict[str, object] = {}
    prompt_sets: dict[int, dict[str, str]] = {}
    candidate_sets: dict[int, list[tuple[int, str]]] = {}
    for held in run_cases:
        manifest, prompts, candidates = build_case(notes, mails, held)
        manifests[str(held)] = manifest
        prompt_sets[held] = prompts
        candidate_sets[held] = candidates
        print("PROMPT_MANIFEST", json.dumps({
            "case": held,
            "decoys": manifest["decoy_note_ids"],
            "phrase_removals": len(manifest["phrase_removals"]),
            "retained_word_counts": manifest["arm_b_retains_any_target_word"],
            "prompt_sha256": manifest["prompt_sha256"],
        }, sort_keys=True), flush=True)

    score_cases = validate_case_maps(run_cases, manifests, prompt_sets, candidate_sets)

    OUT.mkdir(exist_ok=True)
    (OUT / "holdout-manifests.json").write_text(
        json.dumps(manifests, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if args.smoke:
        print(f"SMOKE_OK cases={len(run_cases)} arms=2 conditions=3 candidates=12")
        return

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, __version__ as transformers_version
    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(ranker.MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        ranker.MODEL, torch_dtype=torch.float32, low_cpu_mem_usage=True
    )
    model.eval()
    print("MODEL_INFO", json.dumps({
        "model": ranker.MODEL,
        "model_revision": getattr(model.config, "_commit_hash", None),
        "torch": torch.__version__,
        "transformers": transformers_version,
        "crew_sha256": ranker.CREW_SHA,
    }), flush=True)

    results: dict[str, object] = {}
    for held in score_cases:
        case_result: dict[str, object] = {}
        candidates = candidate_sets[held]
        for arm in ("A", "B"):
            arm_result: dict[str, object] = {}
            for condition in ("purpose", "generic", "swapped"):
                prefix = ranker.chat(tokenizer, prompt_sets[held][f"{arm}_{condition}"])
                scored = rank_scores(model, tokenizer, torch, prefix, candidates)
                arm_result[condition] = scored
                print("AB_RANK", json.dumps({
                    "case": held, "arm": arm, "condition": condition,
                    "rank": scored["rank"], "target_score": scored["target_score"],
                    "best_decoy_score": scored["best_decoy_score"],
                    "margin": scored["target_minus_best_decoy"],
                }, sort_keys=True), flush=True)
            case_result[arm] = arm_result
        results[str(held)] = case_result

    (OUT / "ab-ranks.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("AB_COMPLETE", json.dumps({
        "cases": run_cases, "arms": ["A", "B"],
        "conditions": ["purpose", "generic", "swapped"],
        "candidates_per_case": 12,
    }), flush=True)


if __name__ == "__main__":
    main()
