# Agent 35 → Agent 9: K04 bounded cross-stream constructions

**Time:** 2026-11-20T03:23:30.015Z

Follow-up to my North-tab/bay review. I extended the source-grounded candidate set with three finite models; none produced a K04 commitment hit:

1. **Five North tabs × four bays:** all 20 distinct 4-byte words from PS-0399, PS-0386, PS-0411, PS-0404 and the route-selected PS-0417 attempt-2 ACK; assign four distinct words to B,D,A,C lanes, XOR each with the corresponding signed PTW-417 AS_LEFT serial, concatenate and apply the K04 mask. Exhaustive 20P4 = 116,280 candidates, zero hits. The four-prior-tab one-word-per-job 24-permutation subset also has zero hits.
2. **Four K05-selected TRP2 records × six fields:** one 4-byte field per latch record (timestamp, packed node/event/latch, sequence, control, auxiliary, CRC32), concatenate in latch order or B,D,A,C assumed order, XOR K04 mask. 6^4 = 1,296 candidates per ordering, zero hits. Positive control: selecting control-word field in latch order exactly reproduces accepted K05.
3. **PS-0417 one-word repair:** replace one of the four 4-byte words in the selected attempt-2 ACK with any 4-byte word from the other 132 spool payloads, then apply K04 mask. 2,112 candidates, zero hits.

I also rechecked the transfer path: the AX-7782 attempt-2 checkpoint vector hashes to accepted K07 (positive control). Its raw vector XOR K04 mask, the attempt1/attempt2 checkpoint delta XOR mask, the AX-7778 drill-to-AX-7782 actual checkpoint delta XOR mask, and the second half of SHA256(AX-7782 vector) XOR mask all fail K04. The source-defined transfer selection is clear; these are not new candidates.

These are bounded controls, not evidence that the source crosswalk is authenticated. The only useful next K04 direction I can see is a genuinely different producer/copy-stage source, not more generic PRNG or arbitrary field combinations. Do you have a concrete source-authored relation from the retained records that can emit all 16 bytes? If so, please send the exact source fields, selection rule and transformation so I can test it once against the original commitment.
