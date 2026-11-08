# REC8 cross-slot: fourth-order bytewise GF(256) recurrence

**Agent 34 | 8 November 2026 | exploratory algebraic test; no original matches.**

## Question

Can the eight 16-byte REC8 components be consecutive outputs of one common fourth-order recurrence over GF(256), applied independently to each byte lane? If so, the six accepted components could determine the two missing components without using the disputed physical coupon or the missing final caption.

No surviving source document says that the components were generated this way. This is an exploratory test of a possible cross-slot relationship, following the existing shared-coefficient order-2 and order-3 screens.

The model is:

\[
X_n=aX_{n-1}\oplus bX_{n-2}\oplus cX_{n-3}\oplus dX_{n-4},
\]

with the same four field coefficients in all 16 byte lanes. K04 and K08 are treated as erasures.

## Method

Tested both standard byte-field representations used in the earlier REC8 cross-slot work:

- AES polynomial 0x11B.
- Reed-Solomon polynomial 0x11D.

For natural K01-to-K08 order, the original K05, K06 and K07 values supply three complete recurrence equations per byte lane. When a is nonzero, K05 determines K04 for each lane. The K06 equations constrain c and d across all lanes, and K07 is an additional complete compatibility check. K08 is then calculated from K07, K06, K05 and the reconstructed K04.

The a=0 case is solved separately as a 16-equation linear system for b, c and d. K04 is reconstructed from K06 or K07 when those coefficients determine it. Cases with b=c=0 leave K04 undetermined and cannot produce a recovered pair.

The reverse-direction test applies the recurrence from K07 toward K01. It reconstructs K04 from the intact reverse-order slots and obtains K08 by inverting the recurrence's final step. Reverse models with d=0 are non-reversible and cannot recover K08, so they are not counted as complete candidates.

The solver enumerates all coefficient cases in the specified fields, including zero and nonzero coefficient degeneracies. It does not use either missing-slot commitment to select coefficients. The two original SHA-256 commitments are consulted only after a complete pair has been generated.

## Synthetic controls

The same solver was tested against genuinely generated eight-slot sequences, with K04 and K08 withheld.

- **10 forward controls passed**, covering both fields and coefficient patterns with a=0, nonzero a, zero b/c, and d=0.
- **6 reverse controls passed**, covering both fields and reversible coefficient patterns, including a=0.

Each control recovered the exact planted coefficients and both withheld 16-byte values.

## Original result

| Field | Forward complete models | Reverse complete models | K04 commitment hits | K08 commitment hits |
|---|---:|---:|---:|---:|
| 0x11B | 0 | 0 | 0 | 0 |
| 0x11D | 0 | 0 | 0 | 0 |

No complete K04/K08 pair satisfies the tested common-coefficient fourth-order recurrence in either direction or field. The six known components independently revalidate against their original slot commitments.

## Interpretation and limits

This is a new bounded negative for a shared-coefficient, bytewise order-4 GF(256) recurrence. It does not establish that the eight components are independent. It does not exclude other fields, higher-order recurrences, nonlinear constructions, per-lane coefficients, unknown per-slot transformations, or a source-specific relationship.

No K04 bytes or K08 words were recovered. The original candidate, acceptance data, source archive and verifier remain unchanged.

## Reproduction

Run from the repository root:

    python agents/agent34/rec8_order4_gf256_crossslot_sft.py

The standard-library SFT reads the six known values from candidate.json and both missing-slot commitments from resources/acceptance.json. It includes the planted positive controls and checks both recurrence orientations.
