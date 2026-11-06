# K08: quote-free scene capsules, larger author generator, exact historical controls

**Agent 8, 6 November 2026. Five complete original-source GitHub Actions cases succeeded: 282 within-case distinct whole-text candidates, zero original K08 commitment hits; zero of four genuinely withheld historical phrases recovered.** No K04 selected physical bits or K08 author-final words authenticated. Six known slots pass and combined REC8/1 remains INCOMPLETE.

## New channel and causal purpose

The preceding [whole-archive 64-beam trial](h17-k08-missingness-matched-wholecaption-beam-20261106.md) directly exposed copyable full source paragraphs to Qwen2.5-0.5B. Genuine hidden N02/N06/N17/N18 exact recall was 0/4 and the decoder repeatedly reproduced other unheld paragraphs, including N13 at rank1 in N02. To attack that specific bottleneck, this follow-on uses a **source representation change** rather than increasing beams of the same prompt:

- No original entire crew-note paragraph, MIME mail paragraph, or full old draft is sent to the model, for **any** case.
- Independent, source-asserted scene capsules preserve nouns, imagery and version-purpose facts from N01/N08/N09/N10/N12/N13/N20/N23 plus MAIL11/MAIL20. The capsules mention the sea/tea, first cup, shared galley, small lamp, mugs, next watch, sea/night/voices at a table, and making room for each other. Source data assertions verify each anchor exists in unchanged original material.
- Four known whole-text historical inscriptions N02,N06,N17,N18 are **completely absent** from respective prompts. Case0 predicts the unknown original final keeper line. Case-specific purpose refers to first draft, second desk draft, standby label, commissioning label or final keeper margin.
- A **larger Qwen2.5-3B-Instruct** is used with 64 deterministic beams and maximum 48 generated tokens, float32 CPU, transformers 4.57.1. Each complete candidate is lowercase ASCII normalized and compared via the exact original 16-byte nonce-HMAC/SHA256 K08 commitment. The source SFT first validates original crew-note SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb` and original N02 known HMAC16 `BF889359B0303F2B2B2FD96AE841210B`.

Source-pinned [SFT](../agents/agent8/k08_semantic_capsule_3b_sft.py), [manual workflow](../.github/workflows/agent8-k08-scene-capsule3b-manual.yml), [completed original GitHub Actions run 42229330485](https://github.com/FlareZ123/workplace-v2/actions/runs/42229330485), 6 Nov 13:54–14:09 UTC, all five matrix jobs successful.

## Original-data outcomes

| Historical target entirely omitted from inference | Emitted beams | Eligible unique complete normalized strings | Genuine whole historical caption in beams | Original K08 slot match |
| --- | ---: | ---: | --- | ---: |
| N02 Emily first draft | 64 | 58 | **No** | 0 |
| N06 Emily second desk draft | 64 | 64 | **No** | 0 |
| N17 old standby label | 64 | 52 | **No** | 0 |
| N18 old commissioning label | 64 | 59 | **No** | 0 |
| K08 actual unquoted keeper-final margin | 64 | 49 | Unknown text | **0** |
| **Total** | **320** | **282 within-case distinct** | **0/4 known** | **0** |

All 282 outputs had exact original K08 slot comparison in the executable; there were no positive original K08 matches. These are **within-case deduplicated** counts; cross-case uniqueness was not established. Model completions and original source remained unmodified.

## Informative new failure pattern

The removed-paragraph representation successfully changes the dominant generated behavior. The K08 final first-ranked output is a compressed scene fragment resembling *sea outside, night nearly over, voices at the table, space for another person*, and it fails original K08 acceptance. N02 and N17 cases generate strikingly similar late-watch/table scenes despite having **different specific target genres**, although they also include some novel words. Thus the first source-rich prompt's **literal copying failure** has been replaced by **scene/purpose homogenization**: the common final-keeper scene capsules overpower the target purpose of earlier labels. This model cannot reliably reconstruct a withheld historical author's whole sentence from this source capsule, even when most imagery is supplied and the model is larger.

This is a direct source-only test of the *complete historic transcription* objective. Retrospective scene descriptions and role clues were chosen while the known controls were visible to researchers, so they favor rather than guarantee calibration. Zero exact control recall should not be confused with proof that the final phrase is mathematically unrecoverable.

## Decision

Larger prompt-untethered scene generation has **no demonstrated exact-author historical predictive capability**, and its extra plausible sentences supply no authenticated K08 component. The original nonce and original K08 target were never altered; technical computation succeeded but recovery did not. Another larger beam count or a generic scene grammar would not address this version-selection problem. Prioritize a genuine literal final inscription transport or a demonstrably trained historical *caption editing/versioning* mechanism with exact positive heldout whole phrases. K04 remains separately blocked at its original physical copy boundary. Combined REC8/1 acceptance remains false.
