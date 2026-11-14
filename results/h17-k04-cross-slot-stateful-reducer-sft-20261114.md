# H-17: cross-slot stateful REC8/1 reducer SFT

**Agent 43 | 14 November 2026**

## Question

Does a single stateful reducer map each known slot's previous accepted component plus the current slot's source record to the next accepted component? This is a distinct alternative to per-slot source rules and to the PTW/PS record-ID chain tested separately.

The four complete known transitions are K01→K02, K02→K03, K05→K06, and K06→K07. The missing K04 transition would be K03→K04; K08 follows K07 but its phrase source remains unavailable.

## Method

The read-only, source-pinned test is [`agents/agent43/k04_cross_slot_stateful_reducer_sft.py`](../agents/agent43/k04_cross_slot_stateful_reducer_sft.py). It reconstructs the K07 source from the selected AX-7782 checkpoint records, uses the verified source inputs for K02/K03/K06, and uses the accepted components as previous states.

The bounded common-reducer grid covered:

- 18 output functions: MD5, SHA-1, SHA-256/SHA-512 first and last 16 bytes, SHA3-256 first and last 16 bytes, BLAKE2s/BLAKE2b-128, SHAKE128/SHAKE256-128, HMAC-SHA256 and HMAC-SHA3-256 with previous-component or source key, and keyed BLAKE2s/BLAKE2b with previous-component key.
- Four domain prefixes (none, REC8/1, archive-v1, slot label), four separators, and both previous/source concatenation orders.
- Direct output, one global XOR pad fitted only on the first known transition, or one global additive pad fitted only on that transition.

A shared model had to predict all four known transitions (direct) or all three untouched transitions after calibration (padded). A synthetic planted SHA-256 previous-component chain with a fixed XOR pad served as a positive control. Only if a model passed every known transition were K04 source alternatives tested against the K04 acceptance commitment.

## Result

**1,728 models; zero exact holdouts; no K04 candidate.**

| Measure | Result |
|---|---:|
| Direct models | 576; all scored 0/4 |
| Padded models | 1,152; all scored 0/3 |
| Maximum exact holdouts | 0 |
| Fully supported shared models | 0 |
| Synthetic planted holdouts | 3/3 |
| K04 acceptance hits | 0 |

No model passed the complete known-control gate, so no K04 candidate was promoted. The official candidate and source files remain unchanged.

## Interpretation and boundary

This excludes the specified family of common previous-component/source hash, HMAC, and keyed-BLAKE2 reducers with the tested domain, separator, order, and global-offset forms. It does not exclude every conceivable shared export/reducer relation, and it does not prove that the slots are statistically or operationally independent.

The result argues against continuing with arbitrary variants of this same chain family. A further attempt should introduce a genuinely new source-derived stage or a complete model with predictions for untouched historical controls. K04 and K08 remain unresolved.
