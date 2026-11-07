"""Natural-language 4-gram sieve on original-source-compatible n32 raw ASCII seed.

This is an exploratory cross-source *language* test, not a proof of the
historical printer/keeper relationship. The source-literal ASCII constraints
are exact; membership in a public-domain English 4-gram vocabulary is a
heuristic whose coverage is checked on unseen real crew captions.

Original ACK2 copy, K04 digest, K08 nonce/commitment and candidate absent.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re

from k04_n32_remaining_phase_crack_sft import (
    OFFSET, OPEN, mt, words, original_native, n32_source_term_constraints,
    rawkey_allowed, PRINTABLE
)
from k08_noyes_literary_source_sft import fetch_book, BOOK_IDS

ROOT = Path(__file__).resolve().parents[2]
HASHES = {
    30501: "3e5588432f79238db9981beb4eda71296d7b23d3cbec73148fa194c8ded378cf",
    30599: "a29d7154a71073d0037ffffeaa2fcca3440778a73c982d55b6e9ba4449bf192c",
    43186: "5293ddb4075785ac138ac01ecb2ad5f4e3154a7ed84d0bb31b762b90c2404d5d",
}
HOLDOUT = [
    "The sea looks different when you have finally finished your tea.",
    "A good watch leaves the room ready for the next pair of hands.",
    "The little lamp stays on until the corridor has gone quiet.",
    "Nobody should have to make their first cup alone after a bad night.",
]


def corpus() -> set[str]:
    texts = []
    notes = (ROOT / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_text()
    mails = sorted((ROOT / "resources/evidence/mail").glob("*.eml"))
    texts += [notes] + [p.read_text() for p in mails]
    for book in BOOK_IDS:
        _, source_sha256, source_text = fetch_book(book)
        assert source_sha256 == HASHES[book], (book, source_sha256)
        texts.append(source_text)
    text = "\n".join(texts).lower()
    for literal in HOLDOUT:
        text = text.replace(literal.lower(), " ")
    normalized = re.sub(r"\s+", " ", text)
    return {normalized[i:i + 4] for i in range(len(normalized) - 3)}


def holdout_stats(grams: set[str]) -> None:
    for text in HOLDOUT:
        chunks = [text[i:i + 4].lower() for i in range(0, len(text), 4)
                  if len(text[i:i + 4]) == 4]
        missing = [(i * 4, chunk) for i, chunk in enumerate(chunks)
                   if chunk not in grams]
        print("GENUINE_HELDOUT_4GRAM", len(text), len(chunks),
              "missing", missing, flush=True)


def phase_screen(native, symbolic, k: int, grams: set[str]):
    observed, _ = n32_source_term_constraints(native, symbolic, k)
    result = {"k": k, "term_count": len(observed), "lengths": {}}
    for length in (61, 62, 63, 64):
        failed = []
        winners = []
        for at, (idx, free, terms) in observed.items():
            raw = [word.to_bytes(4, "big") for word in terms
                   if rawkey_allowed(word, idx, length, PRINTABLE)]
            pad = 64 - length if idx == 31 else 0
            # Partial first chunk has no full four-byte language requirement.
            wordlike = [chunk for chunk in raw
                        if pad or chunk.decode("ascii").lower() in grams]
            if not wordlike:
                failed.append({"at": at, "key_index": idx,
                               "free": free, "printable": len(raw)})
            else:
                winners.append({"at": at, "key_index": idx,
                                "n_words": len(wordlike),
                                "examples": [repr(w.decode("ascii")) for w in wordlike[:4]]})
        result["lengths"][str(length)] = {
            "english_4gram_full_compatible": not failed,
            "english_4gram_at_most_one_uncovered": len(failed) <= 1,
            "failed_source_terms": len(failed),
            "first_two_failures": failed[:2],
            "possible_original_4gram_fragments": winners
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, required=True, choices=range(8))
    args = parser.parse_args()
    grams = corpus()
    print("CORPUS_ORIGINAL_PLUS_3_PINNED_BOOKS", len(grams), "4grams", flush=True)
    holdout_stats(grams)
    native = original_native()
    symbolic = words(OFFSET + 623)
    selected = OPEN[args.shard * 8:(args.shard + 1) * 8]
    exact = {str(length): [] for length in (61, 62, 63, 64)}
    tolerant = {str(length): [] for length in (61, 62, 63, 64)}
    for k in selected:
        result = phase_screen(native, symbolic, k, grams)
        print("ORIGINAL_LANGUAGE_SEED", result, flush=True)
        for length, item in result["lengths"].items():
            if item["english_4gram_full_compatible"]:
                exact[length].append(k)
            if item["english_4gram_at_most_one_uncovered"]:
                tolerant[length].append(k)
    print("SHARD_COMPLETE", args.shard, "phases", list(selected),
          "english_all_terms_phases", exact,
          "english_allow_one_missing_term_phases", tolerant, flush=True)


if __name__ == "__main__":
    main()
