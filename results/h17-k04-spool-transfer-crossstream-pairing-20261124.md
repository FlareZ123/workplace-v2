# K04 spool/transfer cross-stream constructions

**Agent 50 · 24 November 2026 · bounded negative result**

## Question

Could the missing 16-byte ESC-N coupon be reconstructed from a relationship between the selected printer packet and the final archive-transfer receipt chain, rather than treating either record as a standalone source?

This is a speculative copy/transfer-stage hypothesis. The retained sources do not explicitly join PS-0417 to AX-7782: MAIL-13 describes the handoff print as carrying a reference and receipt chain, not the whole archive. The test was therefore designed as a bounded falsifier, not as an asserted production rule.

## Source selection

- Printer side: the unique PS-261003-0417, attempt 2, ACK, RECOVER, bench packet selected for ESC-N.
- Transfer side: the eight AX-7782 attempt-2 checkpoint fields in sequence order, consistent with the committed K07 chain.
- Controls: all 133 retained printer packets and all eight complete transfer chains (four transfer IDs × two attempts).

The original route mask, acceptance commitment, verifier and canonical candidate were read but not modified. No candidate bytes or derived component hashes are emitted by the reproducer.

## Candidate families

The source-pinned reproducer tests three complete 16-byte construction families:

1. **Aligned pairwise algebra:** all printer-packet/transfer-chain pairs, forward and reversed chain order, native and per-checkpoint byte order, and 16 aligned XOR, bytewise, 16-bit and 128-bit add/subtract operations: **68,096 candidates**.
2. **Two-byte chunk selection:** for the selected PS-0417/AX-7782 pair, all 256 selectors choosing one of the two-byte chunks from either source at each of eight positions.
3. **Byte interleaving:** for the same selected pair, all 131,072 choices of one byte from each two-byte pair in each source, with both P/C and C/P emission order.

## Result

The source-pinned script completed with all source pins and synthetic positive/negative controls passing.

- Pairwise algebraic candidates: **68,096**
- Selected-pair two-byte chunk candidates: **256**
- Selected-pair byte interleavings: **131,072**
- Total complete candidates: **199,424**
- Original K04 commitment matches: **0**

No K04 candidate was promoted. The combined REC8/1 result remains incomplete.

## Interpretation and limits

This rejects only the tested aligned arithmetic and chunk-interleaving relationships between the retained printer and transfer records. It does **not** show that the physical coupon is absent, authenticate the ACK2 payload, or rule out an unpreserved native spool/host-stage transformation. It also does not test the separate, source-gated mug-stock workbook hypothesis.

The useful next evidence remains the native PS-0417 spool/queue record and independent physical-output witness, or the original profile-refresh source package containing the native workbook and WN-14/photo sidecars. Do not expand this into arbitrary cross-stream permutations without a new source-authenticated relationship.

## Reproduction

Run the following from the repository root:

    python agents/agent50/k04_spool_transfer_crossstream_sft.py

The script pins the four input files by SHA-256, prints aggregate counts only, and includes a planted positive/negative reducer control. It does not print source component values, the K04 mask, candidate bytes or acceptance digests.
