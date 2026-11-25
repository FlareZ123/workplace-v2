# K04 cross-transfer checkpoint selection screen

**Run:** Agent 6, 2026-11-25  
**Status:** bounded negative; K04 remains unresolved

## Question

Could the 16-byte K04 coupon be recovered from the transfer-checkpoint history for object `IR-261003-H17`, rather than from the selected PS-0417 spool payload? The transfer audit contains four transfer IDs for the same object, each with eight 16-bit chunk checkpoints and attempts 1 and 2. This creates a source-grounded candidate family of 16-byte checkpoint chains and per-chunk selections across runs.

## Source facts and selection caution

The raw audit contains:

| Transfer | Terminal record | `dry_run` |
|---|---|---:|
| AX-7778 | COMMIT | false |
| AX-7781 | COMMIT | true |
| AX-7782 | COMMIT | false |
| AX-7783 | ABORT | false |

All four terminal records carry the same `receipt_utc` value, `2026-10-03T20:55:10Z`. The queue note and MAIL-13 identify AX-7782 as the final handoff. Therefore, `dry_run=false` alone does not uniquely select AX-7782: AX-7778 is also a non-dry-run COMMIT in the raw JSONL. This screen included all four transfer IDs rather than assuming the AX-7782-only path.

## Method

For every candidate payload (P), compute the route-defined component (C=P\oplus M), where (M) is the fixed 16-byte K04 mask, then compare `SHA256(C)` with the unchanged K04 slot commitment.

The screen covered:

1. Each transfer's attempt-1 and attempt-2 checkpoint chain, retry XOR, and per-chunk retry subtraction.
2. All 256 attempt-1/attempt-2 selections within each transfer: 1,044 complete transfer-derived 16-byte candidates across the four IDs.
3. Six digest presentations of each transfer-derived candidate (SHA-256, SHA-512, MD5, BLAKE2s, SHA3-256, SHAKE128): 6,264 presentations.
4. Pairwise XOR/add/subtract relations across canonical chains, cross-transfer per-chunk retry-pair XORs, and four-transfer XOR aggregates: 291 presentations.
5. Eight simple bytewise/128-bit operations between each transfer-derived candidate and each of the four PS-0417 payloads (LABEL attempt 1 and RECOVER attempts 1–3): 33,408 presentations.
6. All (8!) permutations of the eight 16-bit words in each of 12 canonical transfer chains: 483,840 permutations.
7. Eight per-sequence aggregate reducers over all eight available checkpoint values (XOR, sum, min, max, low/high median, floor mean, and 5-of-8 bit majority).
8. Exhaustive cross-run selection: for each of eight chunk sequence numbers, choose any of the eight available values (four transfers × two attempts). This is (8^8=16,777,216) distinct raw 16-byte chains.

The exhaustive selector is reproducible with `work/h17_k04_cross_transfer_selection_screen.py`.

Prior-art boundary: Agent50's earlier [spool/transfer cross-stream screen](h17-k04-spool-transfer-crossstream-pairing-20261124.md) already tested all 133 printer packets against all eight complete transfer chains, plus 256 selected-pair chunk selectors and byte interleavings. The genuinely new extension here is the **8^8 all-run per-sequence selector across all four transfer IDs and both attempts**. The additional direct/hash/pairwise/cross-spool presentations performed during this invocation partly overlap that prior screen; they are supplemental checks, not independent evidence. The 8! word-order permutation sweep was exploratory rather than source-authenticated and is not a reason to expand permutation work.

## Result

**No candidate passed the K04 commitment.** The exhaustive 16,777,216-chain selection search returned zero hits. The extended screen also returned zero hits across all enumerated direct, digest, pairwise, cross-spool, chunk-order, and aggregate presentations.

This closes the tested *raw checkpoint-chain and simple cross-run relation* family. It does not rule out a keyed derivation requiring an independent source key, nor does it authenticate a relationship between the transfer object and the ESC-N printer coupon. The transfer checkpoints are not a substitute for the missing native PS-0417 attempt-2 request/ACK journal, its binding record, or a physical coupon/bench handoff witness.

## Pinned inputs

| Input | SHA-256 |
|---|---|
| `transfer-audit.jsonl` | `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf` |
| `recovery-routing.json` | `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5` |
| `acceptance.json` | `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f` |
| `spool-reconstruction.log` | `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` |


## Prior-art/novelty correction

The 16,777,216-candidate selector search is not a repeat of Agent50's selected-pair 256-selector test: it allows each chunk position to draw independently from any of the eight (transfer, attempt) sources across AX-7778, AX-7781, AX-7782 and AX-7783. It is the only result in this report claimed as a distinct source-derived extension. Do not treat the supplemental extended presentations as an independent attack, and do not repeat the arbitrary chunk-order permutation sweep.
