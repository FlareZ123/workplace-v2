# K08 exact source-vocabulary phrase search (1–4 words)

**Date:** 14 November 2026 UTC  
**Status:** Completed bounded search; no K08 commitment hit.  
**Acceptance impact:** None. K08 remains MISSING; K04 remains MISSING; REC8/1 remains INCOMPLETE.

## Question

Could Emily's missing K08 keeper-envelope phrase be recovered as a normalized sequence of one to four words drawn from the surviving crew noticeboard/desk notes and galley/stores vocabulary?

This is a deliberately bounded source-derived candidate family. It does **not** assume that the final envelope wording must be four words, or that the surviving notes contain every word Emily used.

## Exact acceptance procedure

The search used the unchanged K08 rule in `resources/evidence/recovery-routing.json` and the K08 slot commitment in `resources/acceptance.json`:

1. Normalize a candidate by lowercasing, replacing punctuation with spaces, and collapsing whitespace.
2. Compute HMAC-SHA256 with the raw 16-byte K08 desk nonce as key.
3. Take the first 16 bytes of the HMAC result as the K08 component.
4. Compare SHA-256 of those 16 bytes with the committed K08 slot hash.

No verifier, acceptance value, candidate value, or evidence source was modified.

## Source vocabulary

The vocabulary is the set of unique lowercase alphanumeric tokens extracted from exactly:

- `resources/evidence/crew/noticeboard-and-desk-notes.txt`
- `resources/evidence/crew/galley-and-stores.log`

Both source hashes and the vocabulary cardinality were checked by the C++ scanner:

| Input | SHA-256 |
|---|---|
| Noticeboard/desk notes | `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb` |
| Galley/stores log | `23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46` |
| Sorted 321-token vocabulary (newline-delimited) | `399ddef7c8cce60aa1e78d3ec85683b0188c08b4346ad0bd824d4068d8dc29ba` |

The vocabulary contains 321 tokens. Repetitions are allowed in candidate phrases; word order is unrestricted.

## Results

| Phrase length | Candidates checked | K08 commitment hits |
|---:|---:|---:|
| 1 word | 321 | 0 |
| 2 words | 103,041 | 0 |
| 3 words | 33,076,161 | 0 |
| 4 words | 10,617,447,681 | 0 |
| **Total** | **10,650,703,?** | **0** |

The one-, two-, and three-word spaces were exhaustively checked locally with the exact nonce, normalization and commitment. The three-word C++ scan also checked both source hashes, the 321-token vocabulary, and the historical N02 HMAC control.

The four-word space was exhaustively checked by five parallel GitHub Actions shards in [run 43627068386](https://github.com/FlareZ123/workplace-v2/actions/runs/43627068386), using the existing `agents/agent22/k08_crew_fourword_sft.cpp` scanner and the new manual-dispatch workflow `.github/workflows/agent1-k08-crew-fourword.yml`.

Shard coverage was:

| First-word indices (half-open) | Result |
|---|---|
| [0, 64) | success |
| [64, 128) | success |
| [128, 192) | success |
| [192, 256) | success |
| [256, 321) | success |

Each shard verifies the two source hashes, vocabulary hash/cardinality, a historical N02 HMAC control, complete expected candidate count, and a planted synthetic positive. The scanner exits with code 10 if it finds an original K08 commitment hit and code 2 if coverage or a control fails. All five jobs completed successfully; therefore the complete four-word space was covered, all controls passed, and no original commitment hit occurred.

## Interpretation and limits

This rules out a K08 phrase of one to four normalized words **when every token belongs to the 321-word vocabulary extracted from those two surviving files**. It does not rule out:

- a phrase longer than four words;
- a phrase containing words absent from the surviving notes/galley files;
- wording preserved only on the original envelope, an original card, a native print object, or another missing source.

Do not extend this into a 321^5 sweep or broaden the vocabulary without a new source-defined reason. The next productive step is original evidence acquisition, not more thematic phrase guessing.

## Next K08 witnesses

The direct acceptance witness remains the original recovery-envelope face/margin or an authenticated scan. Additional source-specific locators in `results/h17-missing-evidence-request.md` are:

- the small physical card Zoey says she placed by the shelf beside the chipped blue mugs (MAIL-12), preserved in situ and with both sides;
- the native PS-261003-0323 job object and rendered output, conditionally associated with Emily's N23 note; its note/job pairing is structural until an original queue/job manifest authenticates it;
- the original WN-14 folder and the office profile-refresh/migration package, if an authorized preserved copy becomes available.

These are retrieval targets, not claims that the phrase is present in any one of them. K04 still requires the original PS-0417 attempt-2 coupon/spool evidence and the independently authorized Risk-desk paper-key register. No eight-part candidate is accepted.
