# K04: original PV175–177 MT triple cannot extend to a uniform 112-reading stride-seven history

**Agent 32 | 5 November 2026 | exact original source-only disproof of a stronger continuation hypothesis.** Original printer and historian evidence, commitments, selected escrow coupon and verifier remain unchanged. Six previously accepted REC8 slots remain accepted; K04/K08 and combined REC8/1 are unresolved.

## Why test this particular continuation

The earlier [three-reading original-source bridge](h17-k04-pv-full-affine-lowrank-sweep-20261104.md) found historian sequences 175,176,177 compatible with the hypothetical *p951* printer MT19937 state at native stage indices **−1567, −1560, −1553**, respectively, under the exact CPython 53-bit expression `round(12 + 76 × random.random(),3)`. [The preceding exact-53 analysis](h17-k04-pv176-source-equation-exact53-20261103.md) added one conditional state equation while still leaving 128/128 selected K04 bits free.

The natural but stronger causal interpretation is that the entire original historian `PV` sequence 100..211 was emitted by **one regular seven-native-word producer**, anchored by that three-reading run:

`stage(seq) = -1567 + 7 × (seq - 175)`.

This specific extension deserves a source-only heldout test **before** treating all 112 PV readings as extra printer-state constraints. It was not established by the earlier three matches. Unlike the prior [p955 unknown-affine five-reading epoch screen](h17-k04-pv-unknown-affine-epoch-source-falsifier.md), this test fixes the **p951 original three-reading native anchor and fixed 12..88 producer law**, then uses original readings *outside the three anchors* as heldouts.

## Original data, exact model, and heldout computation

Source SHA256 pins:
- Original spool: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Original historian: `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`.

Exactly 132 printer packet rows (all but selected row129) constrain a fresh **19,968-bit symbolic MT state**, with `ORIGIN=-2092`. Original **p951** printer start positions are reused as a conditional model; the recalculated printer-only GF(2) rank is **15,365**. There is no source-proven historical MT generator or p951 physical print-stage authentication.

For each of the 112 preserved `PV` readings, with recorded millivalue `m=1000×PV`, a claimed exact 3-decimal emitter implies an exact original interval:

`(2m−24001)/152000 ≤ U < (2m−23999)/152000`

where `U=((MT32_stage>>5) × 2^26 + (MT32_stage+1>>6))/2^53` is CPython's 53-bit `random.random()`. The interval fixes **10–16 leading bits** of the first tempered MT output in each reading, without assuming any unobserved lower bits or solving the alleged PV generator in the target's favor. Ask the frozen **printer-only** basis which of those bits it predicts, then count direct contradictions. No failed PV observations are inserted into the state.

## Original results: numerous GOOD-quality direct contradictions

| Original observations | Count | With at least one printer-fixed bit | Contradict printer-fixed bits |
| --- | ---: | ---: | ---: |
| All historian PV seq100..211 | **112** | **44** | **33** |
| `quality=GOOD` | **73** | **31** | **25** |
| `quality=SUSPECT` | 39 | 13 | 8 |
| All PV with **≥8 fixed** bits | **17** | 17 | **14** |
| GOOD PV with **≥8 fixed** bits | **12** | 12 | **10** |

Specific independent original heldouts:
- **PV119**, marked **GOOD**, value **85.111**, hypothetical stage **−1959**: **15 printer-fixed bits, 9 wrong**.
- PV120, GOOD, 12.904, stage −1952: **9 fixed, 7 wrong**.
- PV124, GOOD, 13.940, stage −1924: **15 fixed, 9 wrong**.
- **PV174**, SUSPECT, 41.339, stage **−1574** immediately before the reported triple: **3 fixed, 2 wrong**.
- Three *known anchoring* rows reproduce their previous source consistency: **PV175: 15/15**, **PV176: 11/11**, **PV177: 13/13** compatible, at stages −1567,−1560,−1553. PV177 is itself SUSPECT.
- PV178, GOOD, stage −1546: **zero** frozen printer-fixed bits, so its lack of contradiction has **no evidential force**.

A source-excluded selected printed coupon cannot repair these contradictions: the model's predictions are derived solely from **132 independent source packet copies**, and original quality GOOD rows contradict them directly. The result rejects a **full-sequence constant-stage-seven literal MT float history in precisely the specified p951/fixed-affine model**. It does not refute a *local* three-reading relation, an irregular skip schedule, a different engineering scale, or a different underlying PRNG.

## Independent generated positive and reproducibility

The [single-file reproducible Python SFT](../agents/agent32/k04_pv_triad_seq7_global_falsifier_sft.py) includes an independent seeded real CPython MT19937 stream: it emits 132 synthetic printer packets at the identical stage indexes, hides synthetic selected row129, generates all 112 synthetic rounded PV values at the same seven-word stages, and verifies that **every** original-format synthetic PV agrees with every frozen printer-predicted bit. The original reader checks both source digests and the exact 133-row/112-reading structures.

Completed source-pinned original GitHub Actions [run **42053056232**](https://github.com/FlareZ123/workplace-v2/actions/runs/42053056232) at source revision `2aef81a4` reports:
`ORIGINAL_P951_PRINTER_RANK 15365`;
`ALL_PV 112 with_frozen_printer_bits=44 source_conflicting_rows=33`;
`GOOD_ONLY 73 original PV rows; printer_fixed=31, contradicted=25`;
`SYNTHETIC_REAL_MT_AND_PV_POSITIVE_PASS`;
and `RESULT FULL_112_PV_CONSTANT_NATIVE_STRIDE7_REJECTED`.

**Decision:** do not extrapolate the PV175–177 triple to the entire historian at stage spacing seven to create apparent K04 target coverage. The three compatible original rows can be useful as a local source-consistency clue, but their source-only nonuniformity is now explicit. A future target-reaching bridge needs an independently selected irregular stage schedule or an authenticated original writer/coupon witness. No seventh PASS, authentic selected K04 physical bit or final Emily K08 phrase was recovered.