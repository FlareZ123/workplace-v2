# K04: within-packet linear-code rank check

**Status:** bounded negative; retire the uniform within-packet linear-ECC hypothesis.

## Question

Could the ordinary 16-byte spool payloads share a binary linear code of dimension at most 120, providing at least eight parity constraints that might correct a corrupted selected PS-0417 payload?

## Source and method

Source: `resources/evidence/print/spool-reconstruction.log`, SHA-256:

`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`

The log has 133 chronological 16-byte payload rows. The first 128 rows span 2026-10-03 07:00Z through 17:35Z; the five later rows are the PS-0417 REQUESTED/ACK/REQUESTED sequence, PS-0448 ACK, and PS-0420 RECOVER ACK.

Each 16-byte payload was interpreted as a 128-bit vector. Exact Gaussian elimination over GF(2) used an integer basis keyed by the highest set bit. The affine rank was computed by subtracting the first vector from every subsequent vector before rank calculation.

## Results

| Population | Rows | Linear rank | Affine rank |
|---|---:|---:|---:|
| Chronological prefix | 128 | **128** | 127 |
| Entire spool log | 133 | **128** | **128** |

The 128-row prefix has full linear rank, so it is not contained in any proper linear subspace of the 128-bit payload space. Its affine rank is 127, the maximum possible for 128 points; that supplies at most one affine relation, not the eight or more independent parity constraints required by a dimension-120-or-lower code. Across all 133 rows, even that one affine relation disappears.

## Conclusion and limits

There is no uniform within-packet binary linear code of dimension at most 120 shared by the ordinary 128-row prefix, and no common affine parity subspace across all 133 rows. This closes the proposed uniform linear-ECC route.

The calculation does **not** rule out a nonlinear encoder, a different source-defined late-only cohort, or a separately evidenced corruption process. None is established by the surviving records. It does not recover K04, authenticate the selected ACK2 payload, or change the requirement to bind the native queue/rendered media to the physical ESC-N coupon.

No verifier, candidate, acceptance commitment, or source evidence was modified.
