# K08: complete unique-wordbag permutation of independently selected P20 payload

**Agent 11 · 28 November 2026 · original K08 commitment test · no recovered component**

## Mechanism / research decision

The 28 November AT/MT/ET/PT source-only route independently fixes a 13-token contiguous span of N20 (zero-based words 6..18), SHA-256 `4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c`. This is an authorial semantic payload, but its ordering may be a note-to-final transformation rather than a final inscription. Test the smallest complete word-order reinterpretation with **no invented vocabulary**: preserve all 13 normalized source tokens and their multiplicities exactly, but allow an arbitrary order.

This is **different from Agent14's aligned four-row editor**: that test chooses a word at each fixed *position* from N02/N08/N09/P20, and does not cover every permutation of the P20 vocabulary. Here every candidate uses exactly the same token multiset as P20 and **no other words**.

The source has five copies of one repeated word and eight other singleton words. There are exactly `13! / 5! = 51,891,840` unique complete normalized permutations; no duplicate assignment or target-guided word selection is needed. The arrangement itself is free, not source-selected. This is a conditional **permutation-only** authoring model, not an authenticity claim.

## Reproducibility and controls

- Original note source pinned SHA-256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`.
- Reproducer checks that N20 contains 30 normalized words and that the selected 13-token span matches its previously established SHA.
- Only original recovery-routing `desk_nonce` and unmodified `acceptance.json` K08 commitment are read for the private test. Candidate text and component bytes are never printed, stored or committed. Restricted PDF not read.
- HMAC-SHA256 over the normalized candidate, first 16 bytes, then SHA256 matches the original reducer, checked against the pre-existing N02 first-draft complete-sentence fixture `47e787785ff25082b4b960ad415f1e030ae0edc89c38b2f61c48f9331282ea55`.
- Plant an artificial target digest for the lexically first in-family permutation before enumeration; the complete search must recover the plant **exactly once**.
- The runnable C++17/OpenSSL source includes the original SHA pins and controls, performs no network calls, and reads no original PDF.

## Complete result

Executed locally on the original surviving archive:

```text
K08_P20_WORDBAG assignments=51891840 unique=51891840 planted_hits=1 original_hits=0 source=PASS N02=PASS
real 30.75 s; user 30.69 s
```

Therefore **none of the 51,891,840 distinct possible pure reorders of the 13-token fixed P20 payload passes the unchanged original K08 commitment**. This is a finite, exact full-candidate rejection for the entire original-multiset, word-permutation-only authoring family. It does not reject deletion, insertion, inflection, punctuation changes before normalization, borrowing other words, other source versions, or an independently written final caption.

## Source-fixed vs fitted ledger

| Decision | Status |
| --- | --- |
| P20 source note, span, 13-token multiset, fingerprint | Independently fixed source-only |
| HMAC reducer, desk nonce, original target | Original supplied acceptance/routing |
| Which of the 13 tokens occupies each position | Completely free / exhaustive |
| Required output length and grammar | Exactly 13 normalized tokens; only direct word order |
| Independent historical authored positive control | N02 first-draft HMAC reducer PASS (validates cryptography, **not** authoring model) |
| Planted in-family complete-message control | Exactly one recovered hit |
| Original K08 commitment | **0 / 51,891,840** |

The new result closes a distinct compactness avenue but produces no K08 key. A genuinely solution-producing next experiment needs a **source-selected authoring/version operation** that emits a complete final sentence rather than a larger palette of unconstrained permutations. Preserve the THE/MHI first-/second-draft + shared-photograph lineage as potentially causal, but the exact later-version editorial instruction is still absent.

## Reproducer

`agents/agent11/k08_p20_exact_wordbag_sft.cpp`, build:

```sh
g++ -O3 -std=c++17 agents/agent11/k08_p20_exact_wordbag_sft.cpp -lcrypto -o p20_wordbag
./p20_wordbag <extracted-original-archive-root>
```

Source path is strictly `evidence/crew/noticeboard-and-desk-notes.txt`; routes and acceptance are read from that same permitted archive root. No source-specific candidate output is emitted.
