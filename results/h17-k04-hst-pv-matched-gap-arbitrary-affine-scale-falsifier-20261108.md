# H-17 historian-to-printer matched-gap bridge: variable timing and arbitrary affine-scale source falsifier

**Agent 1 | 8 November 2026 | New original-data generator discrimination.** No K04 physical bytes or K08 caption words recovered. Six original REC8 components remain individually PASS; combined INCOMPLETE.

## A target-oriented source mechanism

The 112 original historian PV sequence numbers 100..211 and printer first-ACK normal job IDs 0300..0411 have the exact arithmetic relationship **printer job suffix = PV seq + 200**. An apparent shared MT19937 printer stream has conditional p951 packet starts recorded in [Agent49's symbolic source basis](../agents/agent49/k04_p951_symbolic_basis.py). Could the historian PV value associated with each job have consumed two hidden native MT words between that 16-byte printer packet and the next?

This experiment allows **every two-word start inside each matching post-packet gap** rather than a globally fixed interval. It tests two levels of the generator hypothesis: one standard rounded 53-bit affine float law and a stronger *arbitrary-affine-scale* falsifier on selected same-tag/same-unit source readings.

The exporter documents PV as engineering-context readings. No original source authenticates the shared RNG, its timestamp ordering, the +200 relation as a data dependency, or this float conversion. All deductions below are conditional.

## Read-only original-source execution

Original spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. Historian SHA256: 3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f. The disputed 18:02 ACK2 row129 is excluded entirely before rebuilding the original **rank-15,365** MT GF(2) source basis. There are 112 distinct matched 2-word gap windows totaling **277 candidate word-pair starts**.

### Complete variable-gap standard float model

For each original historian PV millivalue m, the hypothetical producer y=round(12+76*U53,3) gives the exact integer interval for the two 32-bit MT outputs, with U53 the ordinary CPython 53-bit construction. Compare the source-fixed first-word bits at *every* allowed position against this interval, without filling unknown target or producer bits. **29 of the 112 original PV records have zero compatible starts**, including **18 tagged GOOD**. Representative exact failures: seq102/job0302 sole start20 disagrees in 9 of 15 fixed required bits; seq155/job0355 three starts412–414 disagree in 4,13,11 fixed bits. This falsifies the whole originally aligned two-word-in-gap, fixed 12+76 rounded-float producer. Some of the other 83 records have only source-unconstrained window placements, so their compatibility is not a positive source bridge.

### Stronger arbitrary affine-scale contradiction

Take three original **GOOD FT-13/degC** historian records whose matched printer packet gaps are exactly two native outputs long, leaving a single possible start each. The symbolic printer source fixes the **first 27 high output bits at every one of these three starts**, making the resulting 53-bit uniform U range narrower than 2^-27 for each. The second MT word is deliberately allowed to vary completely.

| Historian seq / printer job | Native gap start | U interval (approximately) | Observed GOOD PV |
| --- | ---: | ---: | ---: |
| 211 / 0411 | 835 | 0.07168 | 67.218 degC |
| 133 / 0333 | 248 | 0.50152 | 25.557 degC |
| 180 / 0380 | 606 | 0.68135 | 65.433 degC |

As the possible original MT uniform U increases, the observed PV values **fall sharply, then rise sharply**. This also excludes **every common monotone scalar conversion** from these three source-fixed uniform intervals to the three GOOD FT-13/degC readings, including nonlinear monotone calibrations. In particular, no single real affine producer **PV = A + B*U** can do this, regardless of the sign or magnitude of B, even accounting for 0.001 rounding. The U intervals are mutually disjoint in this displayed ordering. This contradiction does **not** assume the prior 12+76 scale, any historical pressure/temperature unit mixing, a fixed stream stride, or any selected K04 copied bytes. All three readings have the *same* original tag and unit, avoiding artificial cross-instrument calibration.

A synthetic positive constructs rounded y=12+76*U from these exact original-source U lower bounds, reproducing a monotone 3-row emitter with source-fixed stages. An independent full affine-feasibility calculation in scipy across 46 one-start rows likewise rejects the same three-row GOOD/FT-13/degC subgroup for both positive and negative slopes.

## Next-step consequence and limits

The exact +200 sequence crosswalk, by itself, cannot be promoted into a shared-printer MT producer or a donor for the selected attempt-2 coupon: a single common affine historian emitter fails on original intact same-instrument rows under the matched-gap schedule. A highly nonlinear transformation, per-row reseeding, unobserved stage outside the matching gaps, or an independent historian generator remains possible.

This is distinct from prior same-packet direct PV-to-payload quantizers and fixed-seven-stage historian tests. [Portable Python source-pinned SFT](../agents/agent1/k04_hst_pv_gap_affine_triple_sft.py) recomputes the original printer basis and both contradictions. Original routing, evidence and verifier remain unchanged.
