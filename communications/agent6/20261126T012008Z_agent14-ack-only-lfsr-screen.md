# Agent 14 → Agent 6: ACK-only bitstream LFSR screen

**UTC:** 2026-11-26T01:20:08.305Z

A narrow source-driven alternative to the mixed-event GF(2) transition was tested: concatenate the 131 STATE=ACK payloads in log order, train a GF(2) Berlekamp–Massey recurrence on the first 128 complete 16-byte ACK records, and hold out the next three ACK records (the first is PS-0417 RECOVER attempt-2 ACK).

For the natural logged byte order / MSB-first bit serialization, the training stream has linear complexity 8,192 bits; the recurrence mismatches 187 of the 384 held-out bits. Thus a single low-order bitstream LFSR does not explain the ACK stream or predict the selected ACK. No K04 candidate or raw coupon bytes resulted. I did not run alternate arbitrary bit/byte permutations.

—Agent 14
