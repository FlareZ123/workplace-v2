# K04 complete retry-word XOR production hypothesis

**Agent 5, 2 November 2026.** Test an alternative upstream printer coupon producer rather than arbitrary damage to the selected ACK.

Four original records share the exact selected job PS-261003-0417: early LABEL/ACK attempt1, 18:01 RECOVER/REQUESTED attempt1, 18:02 RECOVER/ACK attempt2, and 18:03 RECOVER/REQUESTED attempt3. Hypothesize a retry-delta or accumulated print-buffer encoding: each of the four output 32-bit words is the bitwise XOR of a nonempty subset of the corresponding four source words. Independently choose 15 possible subsets for each word, optionally reverse the four bytes inside each output word, and reorder the four words.

This differs from Agent16's same-position 4-source byte **selection** search (4^16 possibilities); the present model generates bytes absent from the original four buffers through XOR combination. It is also distinct from one unknown 32-bit repeated XOR correction of the selected ACK. Neither the retained source nor firmware authenticates an XOR-delta producer. Source spool checksum SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

Search: 15^4 subset assignments x 2^4 word endian assignments x 24 word orders = **19,440,000 complete source-derived coupons**. For each, XOR with unchanged mask `8556C8CB6140A7F9A5123AC7571BEE1C` and compare SHA256 of the 16-byte result to the original K04 commitment. The [read-only C/OpenSSL reproducer](../agents/agent5/k04_retry_word_xor.c) includes an independently planted full candidate, which the search recovers.

Actual local complete run:
```
tested=19440000 synthetic_hits=1 original_hits=0
```

**Conclusion:** no complete coupon in this exact four-record, per-word XOR-subset/byte-reversal/word-reordering model matches K04. This excludes a restricted source-based retry-delta production mechanism. Unknown bytes, different temporal producer ordering, other donor sources, damaged copies, and other functions remain outside it. K04 and K08 still unresolved; six previously accepted slots and the canonical evidence/verifier remain unchanged.
