# K04: rounded telemetry PV readings as conditional MT float carriers

**Agent 34 | 3 November 2026 | Original-source producer fingerprint negative.** A different original-source datatype and generator operation from the existing diagnostic-word, recorder-CONTROL and AX-halfword tests. **No authentic selected K04 bit or keeper-caption word recovered.**

## Mechanism and data

The surviving historian includes 112 floating-point `PV` readings, with units degC, kPa or percent and numerical values within 10..90, rounded to 0.001. These readings are explicitly called engineering context in the original telemetry README, rather than raw unsigned diagnostic words. Test a *hypothetical* source-generation mechanism: `round(10 + 80 * rng.random(), 3)` with the standard CPython MT19937 **two-consecutive-output** 53-bit `random.random` construction. Such a number could reveal about sixteen bits of a stream at a known phase and, under a different source-selected index, might be a high-width donor for the p951 target quotient. There is no historical producer evidence for this assumption.

A distinct discrete hypothesis uses `10 + rng.randrange(80000) / 1000`, whose accepted code comes from `getrandbits(17)`. That would be potentially informative at p951 +724 **if independently source-indexed**, because the original [target width threshold](../communications/broadcast/20261103T0252Z_agent5-K04-donor-observation-width.md) requires at least seventeen upper tempered bits there.

## Source-only test

[Reproducer](../agents/agent34/k04_telemetry_pv_floats_sft.py) pins the original historian SHA256 `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`; imports [Agent2's SHA-pinned p951 printer-only closure](../agents/agent2/20261102_k04_multicarrier_p951_sft.py), excluding selected spool packet row129. Of 145 historian rows, 112 are PV. In native stream window -1100..1039, 811 full printer-derived MT words and **584 consecutive full-word pairs** are source-fixed.

For each complete pair, temper both native words and construct precisely the CPython float
`((a>>5)*2^26 + (b>>6)) / 2^53`. Compare the 0.001-rounded hypothetical PV against all 112 original values, preserving the source row, tag and units. Independently compare the high seventeen output bits of every one of 811 complete words to `1000*(PV-10)`, the exact accepted code under the integer-lattice model.

| Producer hypothesis | Original readings | Source-index candidates | Exact observed coincidences |
| --- | ---: | ---: | ---: |
| Two-word `round(10+80*random(),3)` | 112 | 584 consecutive pairs | **1**, native index526 vs historian row12 FT-13/kPa 69.183 |
| One-word `10+randrange(80000)/1000` | 112 | 811 full words | **0** |

As a rough independent-uniform null check for the float model, the expected hit count is `112*584/80000 = 0.8176`, consistent with the single hit. Thus the solitary numerical match is no producer-stage identification or evidence that the real source uses this generator. Both original data carriers and all source masks are immutable. The SFT additionally checks **100 actual CPython `random.random` synthetic controls** against the exactly reconstructed two-word float output.

## Scope and next move

These tests cannot exclude differently rounded/affine PV formulae, partial-state matches, native indices beyond 1039, nonconsecutive source words, a separately seeded generator or a source-ordering rule not present here. In particular, simply observing a plausible PV number at a postselected MT index does not authenticate an H-17 source relationship. Avoid turning arbitrary numeric conversions into high-width donors without a producer-phase rule that forecasts an intact original record first.

The target-selected packet 951..954 remains completely unknown in the printer source closure (128/128). The K04 printed media original is absent, and K08's final Emily caption remains unquoted. Official REC8 state remains six component PASS, K04/K08 unresolved, combined INCOMPLETE.
