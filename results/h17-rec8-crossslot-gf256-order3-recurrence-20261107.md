# REC8 cross-slot: third-order bytewise GF(256) recurrence

**Agent 1 | 7 November 2026.** Exploratory model test. No source document currently states that the eight components form a recurrence; this test asks whether a compact common-source relation could nevertheless recover both erasures.

## Hypothesis

Treat each 16-byte slot as 16 parallel byte lanes. In each lane, the eight slot values are successive terms of one common third-order linear recurrence over GF(256):

\[
X_n=aX_{n-1}\oplus bX_{n-2}\oplus cX_{n-3}.
\]

The coefficients \(a,b,c\) are shared across all 16 byte lanes. K04 and K08 are the two erased terms. This is distinct from a degree-5 Reed-Solomon interpolation and from the previously tested second-order recurrence.

Tested both common byte-field representations:
- AES polynomial \(x^8+x^4+x^3+x+1\), encoded as 0x11B;
- RS polynomial \(x^8+x^4+x^3+x^2+1\), encoded as 0x11D.

Both the natural K01→K08 order and the reverse K08→K01 order were tested. In the reverse direction, K08 is recovered by inverting one recurrence step; that requires \(c\ne0\).

## Method

The six accepted 16-byte values are read from candidate.json and pinned in the SFT. The K04 and K08 SHA-256 commitments are read from acceptance.json and pinned.

For the natural order, K01, K02, K03, K05, K06 and K07 constrain the common coefficients. For each nonzero pair \(a,b\), the first compatibility equation determines \(c\) from any byte lane with a nonzero denominator. Every candidate is then checked against both independent compatibility equations in all 16 lanes. Cases with one or more zero coefficients are solved separately. The three two-variable degenerate systems have rank two on the original values, so those cases are also exhaustive.

The reverse-order test applies the same solver to K07, K06, K05, K04, K03, K02, K01, then inverts the recurrence to recover K08. This tests a separate sequence orientation rather than merely reversing byte order.

## Result

**No solution.**

| Field polynomial | Natural order solutions | Reverse order solutions that recover K08 |
|---|---:|---:|
| 0x11B | 0 | 0 |
| 0x11D | 0 | 0 |

There is no shared bytewise third-order GF(256) recurrence in either tested field that produces the six accepted components while recovering both missing slots.

The SFT includes **14 planted synthetic controls** spanning both fields, forward and reverse orientations, and nonzero/degenerate coefficient patterns. All 14 recovered the planted K04 and K08 values. The original-data solver returned zero solutions in both fields.

## Reproduction

Run from repository root:

    python agents/agent1/k04_k08_order3_gf256_crossslot_sft.py

The script is standard-library only. It reads candidate.json and acceptance.json, verifies their pinned values, exercises the synthetic controls, and tests the original six accepted components.

## Limits

This excludes only a common-coefficient, bytewise order-3 recurrence over the two named GF(256) representations and the two tested slot orientations. It does not exclude higher-order recurrences, other finite fields, nonlinear constructions, or a source-specific relation. It does not recover any K04 or K08 bytes. The model remains exploratory and should not be treated as an archive rule.
