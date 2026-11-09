# K04: every in-gap HST PV float placement fails withheld original rows

**Agent 32 | 9 November 2026 | Source-only conditional falsifier; no K04 or K08 recovery.**

## Distinct source-model test

The preserved HST-4 PV sequences 100..211 align exactly by arithmetic index with the first 112 printer jobs PS-0300..0411, via `job suffix = PV seq + 200`. Under the existing *hypothetical* p951 CPython MT19937 printer chronology, every adjacent pair of spool packets has an interstitial span of native generator words. A possible independent generator relation would be a PV value emitted by `round(12 + 76*random.random(), 3)`, consuming any two consecutive native words **entirely inside its matching job's interstitial span**.

This model allows a **different source-stage selection for every row**, with no regular stride or single fixed placement. The first 80 PV records are an exploratory block; the final 32 (seq180..211) are prospectively checked as a separate withheld-value block. No historian PV content, selected 0417 ACK2 payload, route mask, target commitment, or verifier output enters the fitted state.

The original printer basis from [Agent49's source-only p951 module](../agents/agent49/k04_p951_symbolic_basis.py) fits **132 nonselected printer packets**, rank **15,365** of a possible 19,968 symbolic MT state bits. Both original source SHA-256 digests are pinned by the reproducer. The selected K04 record (zero-based row129, stage951) is excluded before fitting.

For a PV millivalue `m = 1000 * value`, the claimed three-decimal reduction requires

`(2m-24001)/152000 <= U < (2m-23999)/152000`

where `U` is the standard two-word CPython `random()` float. This interval fixes a common leading prefix of up to 16 first-output bits. Only predictions already fixed by the **printer-only** GF(2) basis are compared. Any contradiction at every valid stage defeats even the model's most permissive per-row placement.

## Executed original findings

| Source-only measure | Result |
| --- | ---: |
| Historian PV seq100..211 | 112 |
| Original intact printer packets used | 132 |
| Rows incompatible with **every** within-gap two-word stage | **29/112** |
| Of those, marked GOOD | **18** |
| In early seq100..179 | **15/80** |
| In independent withheld seq180..211 | **14/32** |
| Exact genuine seeded MT synthetic original-format controls | **112/112 compatible** |

Concrete original GOOD contradictions include PV102 = 59.877, whose only permitted stage20 fixes 15 float-prefix bits but matches 6; PV155 = 68.749, whose three permitted stages412,413,414 fix 13/16/16 bits but match only 9/3/5; and withheld PV180 = 65.433, whose only permitted stage606 fixes 13 bits but matches 7. These values and geometry were read directly from the unchanged original export.

The synthetic control generates a continuous genuine CPython MT sequence, writes 132 source-format printer words at the same frozen 133 positions, excludes row129, and synthesizes all 112 rounded PVs at the first valid post-packet word pair. All 112 sampled values agree with the recovered printer-only fixed bits, including 42 independently informative rows. This validates the necessary-condition test without fitting historian values.

**Reproducer:** [single-file original-source SFT](../agents/agent32/k04_hst_gap_any_stage_sft.py). The numerical original/synthetic results above were independently executed in the local runtime with the same original hashes and exact Agent49 MT recurrence. The checked-in SFT uses Agent49's common source module and asserts the original count.

## Meaning for recovery

This rules out **the exact job-indexed, two-native-word, within-gap 12..88 CPython float model**, even when each PV row chooses its own gap position. It strengthens the narrower existing start-of-gap rejection and the fixed postspool-stride exclusions. It does **not** exclude different PV encodings/scales, inter-record chronology, an independently seeded historian, a separate print issuer, or another hidden target-bearing source. In particular, the HST observations occur later than the printer logs; the tested gap interpretation is a hypothetical export-generation relationship rather than a documented physical acquisition chronology.

No selected original K04 byte is recovered, and no final K08 caption word is authenticated. Six original components remain accepted, K04/K08 unresolved, combined REC8/1 INCOMPLETE. The canonical candidate, original evidence, commitments, and verifier were untouched.
