# K04 cross-slot split-digest candidate family

**Date:** 2026-11-26  
**Status:** bounded negative; no recovery component produced.

## Question

Could the K04 coupon be either 16-byte half of a SHA-256 digest over one of the six already accepted source blocks, with the published K04 route mask applied afterward?

This is an exploratory cross-slot relationship. No source record states that K04 reuses another slot's source block.

## Source mapping and positive controls

The reproducer reconstructs the accepted inputs using the same selection rules as `resources/work/recover_six.py`:

- **K01:** raw WN-14 component.
- **K02:** eight LT-204 `DIAG_WORD` values, GOOD/HOLD, selected interval, latest revision per sequence.
- **K03:** signed PTW-417 CLOSED/AS_LEFT serials in B,D,A,C order.
- **K05:** CRC-valid TRP2 node49/event82 control words, latest sequence per latch in the specified eight-second window.
- **K06:** Rev-C RC-17 footer strips in DRAIN,ISOLATE,PURGE,VERIFY service order.
- **K07:** latest committed AX-7782 checkpoint for each sequence 0..7.

Before candidate generation, the script verifies that these six reconstructions reproduce all six original accepted slot commitments. **All 6/6 positive controls passed.**

## Candidate construction

For each of the six source blocks (B_i):

1. Compute (D_i = operatorname{SHA256}(B_i)).
2. Treat both (D_i[0:16]) and (D_i[16:32]) as possible K04 coupons.
3. Apply the exact route operation: (C = 	ext{coupon} oplus 	ext{K04.masked_component}).
4. Compare (operatorname{SHA256}(C)) against the original K04 slot commitment.

This gives exactly **12 complete 16-byte candidates**. No candidate bytes are published by the script.

## Result

- Positive controls: **6/6 PASS**
- Complete K04 candidates: **12**
- Original K04 commitment hits: **0**

The split-digest cross-slot hypothesis therefore does not recover K04.

## Limits

This result excludes only the exact family above: either half of SHA-256 over each of the six accepted source blocks, followed by the unchanged K04 mask. It does not test other hash functions, keyed derivations, multi-source constructions, a different printer producer/copy stage, a corrected mask, or the absent native PS-0417 job/physical coupon. It does not alter the established source interpretation that the ACK2 payload is not an integrity proof.

## Reproduction

From the repository root:

```bash
python agents/agent50/k04_split_digest_crossover_sft.py
```

For an extracted source bundle with the evidence directory at a different path, use `--evidence-root`, `--acceptance`, and `--routing` as documented by `--help`.
