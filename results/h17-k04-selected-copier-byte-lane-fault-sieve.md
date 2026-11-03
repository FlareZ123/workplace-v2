# K04 selected-stage byte-lane and intra-word corruption tests (Agent 9, 3 November 2026)

## Question

Can the original physical/copy-stage mismatch be explained by a **globally structured corruption rule** affecting arbitrarily many of the 16 positions in the selected `PS-261003-0417`, 18:02 UTC, RECOVER ACK2 copied buffer? The inherited random one-, two-, and three-byte repair searches do not, by themselves, exhaust a single shared bitlane error independently activated across *all* sixteen bytes.

The retained packet is `A9A9DC5731A5E2AE879C47215C2559D5` and the original route XOR mask is `8556C8CB6140A7F9A5123AC7571BEE1C`. The intact copied packet XOR mask does not pass the original K04 commitment. No claim is made that this retained packet or these hypothetical failure modes are historically authenticated.

## Complete target-checking experiment

[Executable source-pinned, standard-library SFT](../agents/agent9/k04_copier_bitlane_fault_sft.py). It reads the original immutable spool, route and acceptance files, requires the spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, asserts unique selected-job/attempt/ACK/RECOVER header, and checks each candidate by applying the *unchanged* original route XOR before the untouched slot SHA256 commitment.

**Per-byte independent 16-bit activation masks** (65,536 choices each):

- Eight same-bit-position XOR faults (bitplanes 0 through 7) that may affect any subset of the 16 bytes.
- Per-byte reversal of bit order, high/low nibble swap, full-byte complement, high-nibble complement, low-nibble complement, single-bit circular rotation left or right.

That is 15 × 65,536 = 983,040 complete coupons. A separate full search allows an arbitrary permutation of the four bytes **independently within each one of the four existing 32-bit words**, giving 24^4 = 331,776 possible coupons. Total **1,314,816 full SHA-256 checks**, with **zero authentic K04 matches**.

The SFT also plants synthetic correct physical coupons and uses the **same full XOR-then-SHA acceptance function** to recover cases of mixed nibble swaps, per-byte bit reversals, single-bit faults, and independent four-word permutations. Both false-source and planted-positive scopes are explicit. Duplicate matching transformation indexes are possible when source bytes repeat; the synthetic check requires recovery of the correct coupon bytes, not one unique permutation identifier.

## Limits and next mechanism

The negative is restricted to these 16 physical/copy transformations of one disputed selected buffer. No full original selected coupon is recovered or authenticated. In particular, an unseen intermediate spool object, deletion/insertion errors, longer feedback corruption, per-byte unknown independent values, or a different original route mask remain outside this exact finite search. Earlier arbitrary 1–3-byte failures and byte/word orientation analyses overlap some members of this search; the incremental contribution is the **complete independent per-byte activation family up to sixteen changed positions** with exact original commitment checking and planted full-hash controls.

This should not motivate indiscriminate higher-order bitfault combinatorics. A further test ought to specify a different capture-stage mechanism or a second original comparator that can distinguish a proposed fault source before running it.

Status unchanged: six individual original REC8/1 slots PASS; K04 and K08 unresolved, combined INCOMPLETE.