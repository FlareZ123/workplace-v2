# K04 p951: one 53-bit float for a joint CLASS/DEST printer code

**Agent 36 | 7 November 2026 | new original-source issuer test, no K04 key recovery.**

## Recovery mechanism

Agent23's two-call `randbelow(3)` printer metadata model fails on original fixed rejection witnesses. Its different single-call `randbelow(9)` model also fails. A narrower unused source-generator possibility is a *single CPython `random()` double* consumed as **two consecutive native 32-bit MT19937 outputs**, then `int(random()*9)` mapped by a single unknown bijection to each of the nine original `CLASS × DEST` categories. This would encode both categories in one 53-bit float draw without two separate `randbelow(3)` accept/reject operations.

If such a writer survived authentic untouched ordinary-packet calibration, its native metadata observations might constrain a selected physical coupon under the otherwise conditional p951 source chronology. The original physical printer firmware, the chronological MT hypothesis, and the codebook are not historically authenticated. This test is conditional and uses **no K04 target hash**.

## Original-data source and overinclusive model

The unmodified printer spool SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Reuse the independently committed [Agent49 p951 source basis](../agents/agent49/k04_p951_symbolic_basis.py): all 132 originally retained copied printer packets *except row129*, rank **15,365**. The entire selected row129 is excluded from inference. For each of the **127 consecutive ordinary-source packet gaps**, determine which upper bits of every hidden stage word are fixed by the original source observations.

CPython generates `random()` from **27 high bits of its first word and 26 high bits of its second word**. The nine-way bin is exactly `int(random()*9)`, including binary64 rounding. To make the exclusion conservative, every unfixed source bit is independently permitted to be 0 or 1; the resulting minimum and maximum 53-bit values provide a superset of all possible mapped codes. Unmodeled correlations between unfixed bits can only shrink that set, so they cannot rescue a contradicted whole codebook.

For each interpacket gap, try the first two hidden stage words, last two hidden stage words, and **any adjacent pair** with all other hidden words treated as arbitrary filler. Try four label causal alignments: current/current, current/next, next/current, next/next. For each of these **12 source models**, intersect the allowed nine-bin codes for each repeated original label pair and look for a single injective nine-label codebook. The relaxed any-adjacent case is especially strong because it permits additional unrelated generator draws within every source gap. Exactly **53** original gaps have only two hidden stage words and offer no position ambiguity.

The control replays **2,000 actual Python `Random.random()` outputs** against an independently seeded series of two `getrandbits(32)` values. Additional synthetic checks cover the near-boundary floating-point rounding cases at bin boundaries 2,4,6,8. All pass.

## Original results

| Hidden two-word placement | Current / current | Current / next | Next / current | Next / next |
| --- | ---: | ---: | ---: | ---: |
| First adjacent pair | 1/9 | 0/9 | 0/9 | 0/9 |
| Last adjacent pair | 0/9 | 0/9 | 0/9 | 0/9 |
| Any adjacent pair | 2/9 | 2/9 | 1/9 | 2/9 |

The entries are **number of the nine original category labels retaining at least one possible numeric code after all 127 gaps**, even under independent free-bit overapproximation. A consistent injector needs all nine labels to admit a distinct code. **Zero of the twelve models has such a codebook.**

For example, in the generous any-adjacent/current-current case, original ordinary gap **22** drives the `LABEL/bench` code domain to the empty set under already-observed earlier instances of that same label. In another case, gap **25** eliminates `RECOVER/store`. This is a whole-original-data discrepancy and does not depend on any K04 digest fit.

Exact runnable source: [Agent36 53-bit float SFT](../agents/agent36/k04_joint_float_metadata_sft.py). It also reports training-only domain counts from the first64 intact gaps, the full 127-gap counts and concrete contradiction rows. Its original execution on the unmodified uploaded 46-file archive completed with all controls passing and exact result assertions.

## Consequence

The hypothesized single-53-bit-float metadata writer cannot account for the original categorical observations under the p951 native-stage chronology, **even when any adjacent hidden two-word pair and all nine-code mappings are admitted**. This is a new source-generator-family exclusion relative to the exact two-call and `randbelow(9)` results. It does not prove what generated printer bytes, identify the selected physical coupon, or recover a byte of K04. A wholly different writer, stage chronology, metadata placement, physical-copy substitution, or genuine new historical source remains possible.

The six accepted original components remain K01/K02/K03/K05/K06/K07; K04 and K08 remain missing and the combined REC8/1 key remains INCOMPLETE. The evidence, route, acceptance commitments, candidate and verifier were not modified.