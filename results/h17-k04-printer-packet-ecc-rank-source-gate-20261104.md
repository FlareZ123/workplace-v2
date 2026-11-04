# K04 printer-packet redundancy: source-only byte-field rank and conditional erasure-code exclusion

**Agent 2, 4 November 2026.** The original six REC8 slots remain individually PASS; K04 and K08 are unresolved. This experiment tests a *new candidate-generation mechanism*: reconstruct a damaged 16-byte printer coupon from parity/code redundancy internal to each packet. Source-only tests rule out a broad conventional linear version of that mechanism before any speculative four-byte recovery.

## Why this is distinct

Prior work exhaustively tested selected-coupon byte damage families, modeled hypothetical MT producer states and interpolated the eight already accepted/missing REC8 **slots** as Reed–Solomon symbols. Here the proposed code spans the **sixteen bytes of each printer payload**, not the eight archive slots. A fixed affine byte-linear encoder with fewer than 16 input bytes would put every codeword of a printer class inside a proper affine subspace of GF(256)^16. A systematic or nonsystematic RS(16,k<16) block, its byte permutations, and constant-pad variants all have this property. If the property held on intact ACKs, there could be a target-reaching decoder for a corrupted exceptional ACK without enumerating arbitrary byte replacements.

The original source is `resources/evidence/print/spool-reconstruction.log`, immutable SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The 18:02 UTC selected PS-261003-0417 RECOVER ACK attempt 2 is **excluded** from all fitted ranks. The 130 other ACK records are treated as source samples. The two REQUESTED records are excluded from the main integrity cohort.

## Executed exact ranks

| Cohort | n | GF(2) linear rank / affine rank of 128-bit vectors | GF(256) linear / affine rank in each field |
|---|---:|---|---|
| All nonselected ACK | 130 | **128 / 127** | Not needed |
| RECOVER ACK | 37 | 37 / 36 | **16 / 16** |
| LABEL ACK | 52 | 52 / 51 | **16 / 16** |
| STORES ACK | 41 | 41 / 40 | **16 / 16** |

Both irreducible-field representations `0x11B` (AES) and `0x11D` have exactly the reported 16/16 ranks in *all three* classes. Affine rank uses each cohort's first authentic sample as its origin and subtracts it bytewise by XOR. Hence there is no shared class-specific proper affine **byte-linear** code of dimension k<16 across those ACK payloads, in either field. Ordinary RS(16,8), which could correct four erroneous symbols under its normal decoding assumptions, is contradicted by independent source packets. The argument does not require knowing the RS generator matrix or codeword byte order; every fixed invertible byte permutation preserves rank.

The all-ACK **linear** GF(2) rank is 128, ruling out a homogeneous bit-linear code of dimension<128 common to these ACK payloads. Its **affine** rank is only 127, so it does *not* exclude a 127-dimensional affine bit subspace on the ACK-only cohort. That single fitted parity hyperplane is not independently validated: one original REQUESTED record and the disputed copied selected ACK violate it; the other REQUESTED record satisfies it. Its dense fitted normal `1A4338A53DBC586D3B7BC0F84509CE96` has no identified historical CRC interpretation. Do not claim a recovered selected parity bit on this basis.

## Exact reconstruction controls and limitations

Source-pinned cross-row exploratory Lagrange interpolation separately tested GF(256) polynomials 0x11B/0x11D, degrees <4,<8,<16,<32,<64,<96,<120,<128. It withheld selected row129, using rows131/132 (late nonselected ACKs) as strict controls and rows128/130 (REQUESTED) as weak supplementary checks. **Zero of 16 code predictions reproduced either complete heldout ACK**, and all 16 route-XOR derived complete original K04 commitment candidates were rejected. Synthetic degree-two GF(256) polynomials were recovered exactly at heldout positions, including the missing index. This excludes those *particular chronological-index cross-row code models*, independently of the stronger per-packet affine rank finding.

The primary SFT [k04_spool_ecc_source_rank_sft.py](../agents/agent2/k04_spool_ecc_source_rank_sft.py) asserts the original source hash, selected ACK identity and every displayed rank, using standard Python only. For both GF(256) fields it generates 48 genuine synthetic [16,12] affine-linear codewords; rank is **12**, and a planted parity-byte corruption increases the rank to **13**. This is a positive/negative diagnostic for the rank test.

These source facts do not rule out a nonlinear printer serializer, encryption after an inner ECC layer, different code across jobs, or a distinct exceptional ACK physical-media lineage. Such hypotheses need different observables. The exact target coupon remains unproved, K04 authenticated physical bits remain zero, and the author-final K08 sentence remains unknown.

**REC8 status:** K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING, combined INCOMPLETE. Original source, verifier, commitments, and candidate untouched.
