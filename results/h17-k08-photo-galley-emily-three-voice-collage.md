# K08: original photo, galley and Emily three-voice editorial construction

**Agent 2, 3 November 2026.** A direct complete-candidate search of a source-motivated, still-unattested caption-editing family returned **0 original K08 hits among 58,927,104 assignments**. The original six previously accepted K01/K02/K03/K05/K06/K07 slots stay PASS, K04/K08 MISSING, combined INCOMPLETE. No source, nonce, commitment or candidate was modified.

## Why this mechanism differs

The original 2 October MAIL-14 states Emily's photographs and galley captions were kept with her personal desk notes under the signed folder; original MAIL-11 says those captions informed her wording; N10 records revisiting the photograph after the last cup. These statements make it plausible, without attesting a verbatim final, that she composed a late-watch caption from **one physical photograph fragment + one galley/mug fragment + one of her own desk fragments**.

This is distinguishable from v1 [two-span photo+Emily](https://github.com/FlareZ123/workplace-v1/blob/main/results/k08-photo-splices.py), v1 [three Emily anchors N02/N13/N20](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k08-three-anchor-bound.md), v2 Agent27's **four chronological Emily-only** fragments and v2 Agent21's **free authored semantic rewrites**. The new element is simultaneously requiring three distinct, source-attested **caption genres**, not multiplying connector synonyms or old two-source spans.

## Frozen search class

- Photograph group P: N01 empty-bench/sea/tea and N08 daylight/water photograph.
- Galley group G: N09 first-cup-alone, N11 chipped-blue-mug shelf, N19 bed/mug memory.
- Emily group E: N02 first draft, N06 second draft, N13 lamp-and-mugs reminiscence, N20 sea/night/table intention.

From each original note, remove introductory label before a colon, lowercase/tokenize ASCII, and collect unique 2–8-token contiguous fragments touching its specified anchor vocabulary. Independently sourced fragment counts are **P 69**, **G 139**, **E 256** after per-group deduplication (per-note counts asserted in the reproducer). Combine exactly one from each group, all **six group orders**, independently using either a space or ` and ` as each of two connectors. This gives `69 × 139 × 256 × 6 × 4 = 58,927,104` complete assignments. Apply the unchanged K08 normalized-text HMAC-SHA256 truncation and original 16-byte slot SHA256 commitment.

## Result, source pin and controls

Original crew note SHA256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. Portable standard-library single-file [SFT](../agents/agent2/k08_photo_galley_editor_sft.py) pins this source, verifies the original N02 known HMAC component and its nested commitment digest, checks all source/group counts, and plants a complete three-source caption that is recovered **exactly once**.

A locally executed source-equivalent Python implementation reported:

```json
{"result":"NO_MATCH","complete_assignments":58927104,"original_hits":0,"planted_positive_hits":1,"seconds":68.78}
```

The committed self-contained variant retains the same fragment grammar and acceptance computation; no separate remote execution has been claimed.

**Scope:** Reject only this exact three-genre, exact-source-fragment-plus-simple-conjunction editor. No original final margin, exact final normalized word, or transfer rule has been authenticated. The result cannot adjudicate novel words, paraphrases, other caption sources, or more complex edits. Avoid simply scaling fragments/joiners into a bigger speculative language lottery; prioritize a source-selected final version rule or direct original phrase witness. K04 remains a separate unresolved printer coupon.
