# K04: exact later-first P16 inversion with complete preceding byte-slip coupons

**Agent 7 | 28 November 2026 | synthetic whole-coupon tests and state recovery; original-source scan in progress; no accepted K04**

## Distinct target-reaching construction

[Agent 1's later-first inversion](../agents/agent1/k04_xoropp_laterfirst_backwards_local.py) correctly does not assume that intact REQUESTED1 and REQUESTED3 belong to one continuous printer generator. The intact later REQUESTED3 first two 64-bit output words can instead be fitted to a candidate xoroshiro128++ state, whose unique inverse state transition predicts the complete preceding outputs. Earlier implementations covered 18 whole 64-bit-aligned coupon word windows but relied on the older difficult P12 solver.

This method combines:

1. **Exact P16 zero-witness state inversion**: split all 4,096 P12 partitions into all 16 assignments to extra bits 4..7, using only intact REQUESTED3 two-word packet as the SMT fit, with within-child model blocking until UNSAT and UNKNOWN explicitly open.
2. **Exact inverse xoroshiro128++ transition**: reverse to construct twelve complete source-hypothetical prior 16-byte packets, in the forward chronological order expected by each declared packet serializer. The alleged physical selected coupon must start before REQUESTED3, but neither a same-writer earlier REQUESTED1 nor zero hidden copies is assumed.
3. **Complete 16-byte byte-slip copy-stage candidates**: for nine possible preceding packet-gap bands, test all 16 byte-offset alignments within each band; 144 complete coupon windows per solver state and serializer.
4. **Acceptance first**: XOR the source K04 route mask with each candidate and check the unchanged full original SHA-256 commitment. The intact REQUESTED1 comparison remains a separate optional diagnostic; a mismatch never vetoes a commitment-positive candidate. Any component hit is escrowed outside the repository with chmod0600, and original-source CI is denied.

Under a per-packet BA word serializer, continuous byte-slip windows cannot always be represented by independently repacking two consecutive 64-bit words, so this is not merely renaming Agent1's word-start scan. All byte-offset candidates are full objects, not arbitrarily patched 1-byte donors.

## Executed source-independent controls

[Source-safe executable](../agents/agent7/k04_xoropp_laterfirst_p16_byte_slip.py) has a pure --synthetic mode. An independent local implementation exercised:

- **1,152/1,152** planted 16-byte complete-coupon SHA positives: two independent full 128-bit planted generator states × four byte/word serializers × nine preceding gap bands × 16 byte offsets.
- **1,008** positives are off a 64-bit word boundary, a finite copy-stage extension to the existing preceding-word hypotheses.
- Exact generator transition inverse roundtrips on **10,000/10,000** additional seeded states.
- With an earlier full packet matching the planted prior stream, the independent earlier-replay/commitment joint indicator was present; flipping one bit in that earlier source packet made replay vanish while **the full commitment remained positive**, for all serializer/state controls.
- The known true P16 child of a further source-free planted state was independently solved through Agent7's exact two-output SMT, yielding its complete original 128-bit state, with a terminal UNSAT proof after model blocking at a 5,000ms timeout. The complete coupon scan is therefore compatible with recovered states, not restricted to an external supplied state oracle.

The true P16 calibration child in the last control is derived from the synthetic planted initial state; **this is not** evidence that original printer state bits exist in records. A full 65,536-subcube historical scan is still required for source-complete coverage.

## Historical boundary and next experiment

The source-local runner is set to examine original REQUESTED3 in all parent-major P16 subpartitions, checking the full original commitment and retaining aggregate-only stats. No historical original-commitment hit was established at the time of this report. This later-first, conditional generator/copy-stage model is genuinely distinct from the ongoing firstpacket-forward state search: a historical producer reset, state jump or independent later-request writer could cause one to fail while the other succeeds.

A partition returning UNKNOWN is never excluded. The exact stage/serializer and historical printer-generator identity remain hypotheses. Do not treat synthetic SHA positives as archival recovery.

Six original REC8/1 components remain accepted; K04 and K08 unresolved; combined INCOMPLETE.
