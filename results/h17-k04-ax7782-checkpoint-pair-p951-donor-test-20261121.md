# K04: AX-7782 checkpoint-pair donors under the conditional p951 model

**Status:** bounded negative; no K04 candidate recovered.

## Question

The source-only p951 MT19937 model leaves the selected PS-0417 ACK2 coupon's 128 bits unconstrained by the 132 intact spool packets. Existing gap-observability work shows that eight complete native 32-bit MT words at stages **328–331 and 724–727** are sufficient to determine the target.

AX-7782 has eight chunks and two retained 16-bit checkpoint attempts per chunk: exactly sixteen halfwords, or 256 bits. This experiment tested whether those fields can be arranged into the eight required 32-bit donor words.

This is a source-motivated hypothesis, not a source-attested statement that AX-7782 checkpoints were emitted by the printer's MT producer.

## Inputs and method

The run pins these original files by SHA-256:

| File | SHA-256 |
|---|---|
| resources/evidence/print/spool-reconstruction.log | 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083 |
| resources/evidence/transfers/transfer-audit.jsonl | 32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf |
| resources/evidence/recovery-routing.json | f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5 |
| resources/acceptance.json | 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f |

It reuses agents/agent49/k04_p951_symbolic_basis.py without modifying it. The disputed selected row 129 remains excluded; the base system uses the 132 intact source packets and has rank **15,365**. The original K04 route mask and SHA-256 commitment are applied only after a complete candidate coupon is reconstructed.

The AX-7782 attempt-2 chain is also checked as a positive source-parsing control: concatenating its eight checkpoints in sequence order gives 8947CEDCB9CC73BAB7E87BE63302C5C9, which reproduces the official K07 commitment.

## Candidate constructions

Three natural partitions of the sixteen halfwords were tested:

1. **Pair attempts within each chunk (32 configurations).** Each sequence's attempt-1 and attempt-2 checkpoint values form one 32-bit word. Both attempt orders, both halfword byte orders, both 32-bit word orders, both assignments of sequence groups to the two gaps, and native-versus-tempered interpretations were tested.
2. **Separate attempt vectors (16 configurations).** The eight checkpoints from attempt 1 form one 16-byte vector/four words; attempt 2 forms the other. The two vectors were assigned to the two four-word gaps in both directions, with both byte orders and native-versus-tempered interpretations.
3. **P212 and its complement (16 configurations).** The existing parity selector (attempt 1 on even sequence numbers, attempt 2 on odd) forms one 16-byte vector; the unselected halfwords form the complementary vector. Both gap assignments, byte orders, and native-versus-tempered interpretations were tested.

Across the 64 configurations there were **48 distinct complete candidate coupons**. Every configuration augmented the p951 basis to rank **15,621**, making all 128 target bits observable. All 48 candidates were checked against the unchanged K04 commitment.

## Result

- Configurations: **64**
- Distinct complete coupons/components: **48**
- Complete candidate reconstructions: **64**
- Original K04 commitment hits: **0**
- Synthetic positive control: **PASS**
- Intact original spool packets replayed by the synthetic source-consistent state: **132/132**

The synthetic control sets all nonpivot state variables to zero in a state satisfying the original 132-packet equations, replays all 132 intact packets, then supplies the true native words at stages 328–331 and 724–727. The recovery function reconstructs the exact synthetic target coupon. This validates the GF(2) reconstruction path; the synthetic coupon is not an archive value.

## Interpretation and limits

This closes only the three explicit checkpoint-to-gap mappings above, including the listed serialization and word-interpretation views. It does **not** establish a historical common producer, exclude arbitrary nonlinear or noncontiguous mappings, or disprove other source-bearing observations. The queue note calls the checkpoint fields opaque two-byte values; it does not attest that pairing them yields native MT words. The p951 model itself remains conditional.

No K04 bits were authenticated or recovered. The original source files, acceptance commitments, shared candidate, and verifier were not changed.

## Reproduction

From the repository root:

    python agents/agent1/k04_ax7782_checkpoint_pair_p951_sft.py

The script source-pins the inputs, checks the K07 positive control, reproduces all 64 candidate configurations, validates the synthetic positive control, and emits each candidate's component hash and commitment result.
