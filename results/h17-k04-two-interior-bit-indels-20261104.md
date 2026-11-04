# K04: two arbitrary interior bit deletions and reinsertion, complete original-source test

**Agent 8 | 4 November 2026, 22:40 UTC.** New, source-pinned copy-stage hypothesis tested on the original `PS-261003-0417` 18:02 RECOVER ACK2 payload. **264,257,536 complete assignments, 0 original K04 commitment matches.** Original six accepted slots unchanged; K04/K08 unresolved and combined incomplete.

## Mechanism and prior-art separation

The physical escrow coupon is unverified; the preserved copier buffer is `A9A9DC5731A5E2AE879C47215C2559D5`. The archival N22 note likens the label printer to a fax machine, and MAIL16 explicitly distinguishes ACK receipt from copied-byte integrity. An interior bitstream reassembly fault could delete **two individual bits at arbitrary source bit positions** and insert **two arbitrary individual bits elsewhere**, changing alignments across non-byte boundaries. This does not assume the 16-byte copier buffer is the physical coupon.

Closest finished predecessors: [v1 one-sided 1..23 bit-edge slip](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-bit-boundary-slip.md) preserves all bits except a single edge; [v2 two dislocated *whole-byte* deletions/insertions](h17-k04-dislocated-two-byte-copy-splice.md) allows 2-byte movement but stays on byte boundaries; [v2 one/two nibble splice](../agents/agent49/k04_two_nibble_slip_sft.c) stays on nibble boundaries. This test permits two nonadjacent **bit** edits anywhere, with all intermediate original bits in source order; it is neither those edge shifts nor their byte/nibble splice geometry. It does not cover three or more individual bit losses, bit inversions without displacement, or arbitrary physical coupons.

For each of the `C(128,2) = 8,128` ordered-by-position bit deletion pairs, delete both copied bits, retaining 126 in original order. For each of `C(128,2) = 8,128` final output insertion-position pairs, insert each of four possible ordered 2-bit values. Build a **complete 128-bit proposed physical coupon**, XOR the original `8556C8CB6140A7F9A5123AC7571BEE1C` route mask, and check full SHA256 of the resulting 16-byte K04 component against unchanged `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Executed original result and positive controls

Original source `evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` is verified by the program, as is the unique exact selected row. Original routing mask and acceptance commitment are required unchanged. The implementation recomputes the correct single-padded-block SHA256 compression, confirmed against standard OpenSSL SHA256 for a nontrivial seeded coupon.

Executed C++17/OpenSSL/OpenMP SFT on the user's original attached export, four CPU threads:

```text
SOURCE_PINNED complete_assignments=264257536 original_matches=0 planted_assignments=48 deletion_pairs=8128 seconds=3.712
```

The independent synthetic witness deletes original source bit positions **11 and 53**, inserts at final positions **21 and 77** and sets those new bits to **1,0**. The original full hash target is never used to select positions. Its original-buffer reduction is reproducibly recognized by the enumerator. It appeared in 48 assignments because repeated bit patterns can produce the same resulting coupon under several different deletion/insertion histories; the search counts **assignments**, not distinct recovered coupons. All 8,128 deletion pairs were completed.

The exact, tested standalone source [`agents/agent8/k04_two_nonadjacent_bit_indel_sft.cpp`](../agents/agent8/k04_two_nonadjacent_bit_indel_sft.cpp) was committed as Git blob `ec92a1a08e1d0e7cbc2393f07d90fe4387dd866b`, byte-identical to the local executed source. Independent local source SHA256 `8e863c1c8140b4fdc85cc7cb899d015168884a41d6589f47dceaa1ef0a3087ed`.

## Interpretation

This is a **complete and negative** test of the exactly specified two-bit interior edit mechanism, against the full untouched K04 acceptance digest. It is a direct candidate-construction exclusion, rather than a conditional generator-state rank calculation. It authenticates **zero** original physical coupon bits; the copying-fault mechanism itself was speculative. It does not constrain the author's K08 final caption, remains six original component PASS, and never justifies claiming combined acceptance. Future work should seek an independently evidenced physical copier mechanism or full selected-stage source rather than simply expanding arbitrary edit counts without a causal clue.
