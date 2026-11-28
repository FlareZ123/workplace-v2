# K08: all P20 deletion/reorders with one original-source ROOM addition — 1.953B complete misses

**Agent 11 · 28 November 2026 · original unchanged K08 commitment · controlled full-output lexical extension · no recovered key**

## Mechanism tested

The independently established N20 AT/MT/ET/PT source program selects the normalized 13-token semantic span P20, SHA256 `4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c`. [The preceding all-P20-only complete-wordbag test](agent11-p20-exact-13word-wordbag-20261128.md) exhausted 152,152,845 distinct nonempty deletions/reorders and found zero original K08 commitment hits; therefore any terminal line derived from P20 needs another lexical operation.

The most independently evidenced **single additional lexical item** is **ROOM**. It appears literally in the already-selected Emily-authored **N02 First draft**, and her separate MAIL-11 editorial instruction says the final line should convey people **making room** for each other. The test below makes the narrowest lexical extension of the closed P20-only model: append exactly **one instance of `room` to the allowed multiset**, retaining *zero to five* occurrences of source token `the`, any subset of the eight remaining singletons, and allowing every distinct complete permutation. No other word, plural, verb inflection, source-note fragment or paraphrase is introduced.

This is **not** an authenticated authoring operation: which P20 words Emily retained and where `room` was placed are exhaustively free. It is a strict finite one-word-extension test with a source-supported choice of the only new word, rather than a dictionary guess.

## Exact disjoint search domain

P20 consists of five copies of one token (`the`) and eight other distinct singleton tokens. Let `k` be the number of retained P20 words, allowing `0 ≤ k ≤ 13`. Across all disjoint submultisets and all unique word orderings, the original P20-only model had `152,152,845` **nonempty** complete captions. For each retained multiset, inserting one distinct `room` creates exactly `k+1` distinct complete captions. Including the empty P20 subset (yielding only `room`), the exact denominator is:

```text
sum(P20 nonempty submultisets, (k + 1)*unique_permutations) + 1
= 1,953,290,213 DISTINCT complete normalized captions
```

There is **no overlap** between different source submultisets because the lexical multiplicities, including the one additional `room`, differ. This is a unique-caption count, not merely repeated assignment checks.

No candidate text or component bytes are printed, committed, or shipped to CI. Each complete candidate is reduced under the original desk nonce by HMAC-SHA256, truncated to 16 bytes, then SHA256-hashed and compared against the full unchanged original 32-byte K08 commitment.

## Controls and executed result

- Preserved original crew-note SHA256 **PASS**: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`.
- Fixed original P20 span/token count/sha256 **PASS**.
- N02 source wording contains the selected lexical addition **PASS**; N02's independently published first-draft complete-sentence historical K08 reducer fixture **PASS**.
- Synthetic full-message commitment *planted inside the actual 14-word complete candidate family*: **one exact hit**, confirming end-to-end enumeration.
- Original K08 commitment, unchanged from the original bundle: **0 matches**.

Actual local run using the preserved original extraction:

```text
K08_P20_PLUS_N02_ROOM_ALL_SUBMULTISET_PERMS checked=1953290213 planted_hits=1 original_hits=0 source=PASS N02=PASS
real 782.52
user 1226.75
sys 0.08
```

Four OpenMP threads were permitted; elapsed wall time was about 13.0 minutes on shared compute. The source-driven runner produces only redacted aggregate counts. Neither the source evidence, verifier, acceptance nor canonical candidate was modified.

## Strongest conditional inference

**No complete final caption composed from any number of P20 source words (not exceeding each original occurrence count) plus exactly one copy of the source-supported word `room`, in any order, satisfies the original K08 commitment.** This strictly extends the prior 152.2M P20-only result but does not supersede it as a source hypothesis because the lexical domains differ.

If P20 is a true terminal-authoring input and Emily retained `room` exactly once, then one or more *additional* operations—another new word, inflection/substitution, repeated non-P20 terms, alternate source vocabulary or phrase model—are necessary. It does **not** prove the historical line contains `room`, or that P20 is a true input. It does not address the alternate possibility that a complete author-final text came from other original drafts or photograph material.

Agent42 separately found that `room` is original N02 word position six, and tested the three simplest position-six exact P20 insertion/replacement interpretations (all negative). Those are **covered** by the present broader family when the resulting captions have exactly one `room` and no other novel word. Do not rerun them as independent progress.

## Decision ledger

| Decision | Source-fixed or free |
| --- | --- |
| P20's exact 13-token multiset | Independently source-fixed |
| Single new word `room` | Selected by explicit N02 first draft + MAIL-11 motif before the test |
| ROOM occurrence count | Exactly one, fixed |
| Which P20 words survive | Completely free, exhaustive |
| Placement/order of all surviving words | Completely free, exhaustive |
| Normalization, desk nonce and target | Original unchanged verifier/routing/acceptance |
| Historical N02 cryptographic fixture | PASS, validates reducer not authoring mechanism |
| Planted source-family positive | 1 exact hit |
| Original K08 commitment | **0 / 1,953,290,213** |

## Reproducer

[`agents/agent11/k08_p20_plus_source_room_sft.cpp`](../../agents/agent11/k08_p20_plus_source_room_sft.cpp). Build `g++ -O3 -std=c++17 -fopenmp agents/agent11/k08_p20_plus_source_room_sft.cpp -lcrypto -o p20_plus_room`; run `OMP_NUM_THREADS=4 ./p20_plus_room <extracted-original-archive-root>`. The runner pins the crew source, input span, full expected unique denominator and positive controls. It never reads the hash-only restricted PDF.

**Full REC8/1 still INCOMPLETE: K01/K02/K03/K05/K06/K07 PASS; K04 and K08 MISSING.** The next viable K08 work must select a *whole editorial operation* with all added/substituted vocabulary and positions causally determined by actual surviving records rather than a second free lexical item.
