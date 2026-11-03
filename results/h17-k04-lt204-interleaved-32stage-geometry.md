# K04: 32-value LT-204 revision-interleaved MT chronology gives no future donor stage

**Agent 18 | 3 November 2026 | New source-only p951 ordering test, no authentic selected coupon recovery.**

## Original-source question

The surviving freeze historian preserves **four revision values for each of eight** LT-204 `DIAG_WORD` diagnostic sequence numbers, 32 distinct original unsigned 16-bit values. An earlier [Agent17 p955 probe](../agents/agent17/k04_diag_fixedpad_future_sft.py) examined each revision separately as an eight-sample fixed-stride, optionally masked future MT halfword stream. That does not test a **single interleaved 32-reading producer sequence** in which the four revision values may have been emitted together for each diagnostic `seq`, as distinct from an entire revision run.

Under the established *hypothetical* p951 common-MT19937 printer chronology, test six source-metadata orderings: `seq` then revision, revision then `seq`, acquisition timestamp, file export order, `seq` with reversed revisions, and revision with reversed `seq`. A proposed producer outputs each unsigned 16-bit field as the high or low half of **either native or tempered** MT words, directly or with its two bytes exchanged. Each field consumes a **fixed 1..12 native-output stride** from an unknown start in `-2000..3999`. This is a specific source-producer hypothesis, not company-authenticated historian firmware.

The selected printer row129 is explicitly withheld *before* MT state closure. Neither the K04 route mask, copied selected ACK, K04/K08 commitments nor verifier enter model fitting.

## Source-only computation

Re-use the [source-pinned Agent2 printer-only recurrence closure](../agents/agent2/20261102_k04_multicarrier_p951_sft.py) and its original 132 intact packets (spool SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`). The 32 historical LT-204 records are loaded from historian SHA-256 `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`. This p951 closure derives **968 complete 32-bit native output words** and preserves **zero individually fixed bits** at the missing selected p951 word positions 951..954.

For each 32-reading assignment, compare the first 16 values against only complete source-derived output words whose indices agree with its proposed start and stride; absent source-fixed positions do not count as matches or contradictions. At least **three genuinely source-fixed 16-bit comparisons** (48 exact bits) and zero mismatches are required before a stage/stride is eligible to check the last 16 original readings as heldouts.

| Test quantity | Actual result |
| --- | ---: |
| Original diagnostic values | **32** |
| Source-informed source start/stride layouts (≥3 complete words in training half) | **22,183** |
| Complete order/view/orientation/stride/epoch assignments, including weak-coverage cases | **3,339,936** |
| Maximum exact matching 16-bit readings within any first 16 samples | **1** |
| First-half source-compatible models with ≥3 comparisons | **0** |
| Heldout stage-model predictions / accepted original K04 coupon bytes | **0 / 0** |

The highest exact match of one first-half reading is recorded across all 48 order/view/byte-orientation branches and all candidate start/strides. This rejects the defined **straight 16-bit fixed-stride interleaved-emission model** before any selected coupon hash is considered.

A separate original-source planted-stage control uses the already source-fixed direct-tempered upper 16 bits at native start0, stride1: **10/10** checked first-half readings and **15/15** second-half source-fixed readings match, and one deliberately altered original-control comparison is rejected. The control demonstrates that the matching logic can recognize a valid 32-reading source-derived stream, while unobserved positions remain unspecified. It does not validate a historical telemetry producer.

[Portable source-pinned read-only SFT](../agents/agent18/k04_lt204_interleaved_stage_sft.py) asserts the precise record inventory, source ranks, 22,183 informative geometries, 3,339,936 comparisons, zero ≥3 matches and positive controls. A local source-equivalent implementation completed and returned these numbers; the repository-portable import-based version has not been independently rerun on a remote runner.

## Interpretation

This mechanism differs from the prior revision-major, p955 and unknown fixed-pad tests by ordering **all 32 revisions jointly** and using the source-preferred p951 geometry. It supplies an additional original-data negative for one cross-source target-witness family. It does **not** exclude a time-dependent revision/rejection sampler, variable-length draw gaps, an encoded or transformed diagnostic field, a different MT alignment or an independent recorder. Even a matching first-half stage would still need a causal producer/copy bridge and target-reaching quotient analysis before any coupon bit were authenticated.

No original component or phrase was recovered. **Original K01/K02/K03/K05/K06/K07 remain PASS, K04 and K08 remain MISSING, and combined REC8/1 is INCOMPLETE.** No company evidence, commitments, verifier or canonical candidate was altered.
