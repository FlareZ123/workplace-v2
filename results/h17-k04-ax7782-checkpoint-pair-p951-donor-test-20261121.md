# K04: transfer and cross-slot halfword donors under the conditional p951 model

**Status:** bounded negative; no K04 candidate recovered.

## Question

The source-only p951 MT19937 model leaves the selected PS-0417 ACK2 coupon's 128 bits unconstrained by the 132 intact spool packets. Existing gap-observability work shows that eight complete native 32-bit MT words at stages **328–331 and 724–727** are sufficient to determine the target.

AX-7782 has eight chunks and two retained 16-bit checkpoint attempts per chunk: exactly sixteen halfwords, or 256 bits. K02's telemetry preimage and K07's transfer preimage are also each eight 16-bit values. This experiment tested whether those retained halfword streams can be arranged into the eight required 32-bit donor words.

These are source-motivated hypotheses, not source-attested statements that transfer or telemetry fields were emitted by the printer's MT producer.

## Inputs and method

The run pins these original files by SHA-256:

| File | SHA-256 |
|---|---|
| resources/evidence/print/spool-reconstruction.log | 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083 |
| resources/evidence/transfers/transfer-audit.jsonl | 32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf |
| resources/evidence/telemetry/freeze-export.jsonl | 3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f |
| resources/evidence/recovery-routing.json | f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5 |
| resources/acceptance.json | 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f |

It reuses agents/agent49/k04_p951_symbolic_basis.py without modifying it. The disputed selected row 129 remains excluded; the base system uses the 132 intact source packets and has rank **15,365**. The original K04 route mask and SHA-256 commitment are applied only after a complete candidate coupon is reconstructed.

Two source-parsing positive controls pass:

- AX-7782 attempt-2 checkpoints in sequence order give K07 preimage 8947CEDCB9CC73BAB7E87BE63302C5C9 and reproduce the official K07 commitment.
- The K02 route selects eight LT-204 DIAG_WORD samples meeting GOOD/HOLD and the UTC window, retaining greatest revision per sequence. Packing those values as big-endian uint16 gives K02 preimage E1A5E474BAD7E853A2E8C71D3317D507 and reproduces the official K02 commitment.

## Candidate constructions

Five natural partitions of the available halfwords were tested:

1. **Pair attempts within each AX-7782 chunk (32 configurations).** Each sequence's attempt-1 and attempt-2 checkpoint values form one 32-bit word. Both attempt orders, both halfword byte orders, both 32-bit word orders, both assignments of sequence groups to the two gaps, and native-versus-tempered interpretations were tested.
2. **Separate AX-7782 attempt vectors (16 configurations).** The eight checkpoints from attempt 1 form one 16-byte vector/four words; attempt 2 forms the other. The two vectors were assigned to the two four-word gaps in both directions, with both byte orders and native-versus-tempered interpretations.
3. **P212 and its complement (16 configurations).** The existing parity selector (attempt 1 on even sequence numbers, attempt 2 on odd) forms one 16-byte vector; the unselected halfwords form the complementary vector. Both gap assignments, byte orders, and native-versus-tempered interpretations were tested.
4. **Pair K02 and K07 by sequence (32 configurations).** The K02 telemetry preimage and K07 transfer preimage each contain eight uint16 values. The corresponding values were paired into eight 32-bit words, with both source orders, halfword and word endianness, both gap assignments, and native-versus-tempered interpretations.
5. **Separate K02 and K07 vectors (16 configurations).** Each accepted 16-byte preimage was split into four 32-bit words; the two source vectors were assigned to the two four-word gaps in both directions, with both byte orders and native-versus-tempered interpretations.

Across the 112 configurations there were **80 distinct complete candidate coupons**. Every configuration augmented the p951 basis to rank **15,621**, making all 128 target bits observable. All 80 candidates were checked against the unchanged K04 commitment.

## Result

- Configurations: **112**
- Distinct complete coupons/components: **80**
- Complete candidate reconstructions: **112**
- Original K04 commitment hits: **0**
- Synthetic positive control: **PASS**
- Intact original spool packets replayed by the synthetic source-consistent state: **132/132**

The synthetic control sets all nonpivot state variables to zero in a state satisfying the original 132-packet equations, replays all 132 intact packets, then supplies the true native words at stages 328–331 and 724–727. The recovery function reconstructs the exact synthetic target coupon. This validates the GF(2) reconstruction path; the synthetic coupon is not an archive value.

## Interpretation and limits

This closes only the five explicit halfword-to-gap mappings above, including their listed serialization and word-interpretation views. It does **not** establish a historical common producer, exclude arbitrary nonlinear or noncontiguous mappings, or disprove other source-bearing observations. The queue note calls AX checkpoint fields opaque two-byte values; the telemetry route calls K02 values DIAG_WORDs. Neither source attests that these fields are native or tempered MT words or that their producers share the printer's MT stream. The p951 model itself remains conditional.

No K04 bits were authenticated or recovered. The original source files, acceptance commitments, shared candidate, and verifier were not changed.

## Reproduction

From the repository root:

    python agents/agent1/k04_ax7782_checkpoint_pair_p951_sft.py

The script source-pins the inputs, checks the K02 and K07 positive controls, reproduces all 112 candidate configurations, validates the synthetic positive control, and emits each candidate's component hash and commitment result.
