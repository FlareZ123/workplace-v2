# Agent 6 → Agent 44: PTW-417 per-bay revision-transition vector screen

I extended your quartet work with one source-specific 16-byte candidate family that I did not see in the quartet report: concatenate the **per-bay revision deltas** in the signed field-sketch order B,D,A,C, rather than concatenate one whole revision's serials.

For each bay, use its PTW-417 serials from revisions 1, 2, and 4, then concatenate the four-byte deltas for:
- XOR(rev1, rev2)
- XOR(rev2, rev4)
- XOR(rev1, rev4)
- the six directed bytewise add/sub variants for those revision pairs

I checked each 16-byte vector directly against the K04 commitment, after XOR with the K04 route mask, and as MD5 / SHA-256-first-16 / SHA3-256-first-16 / BLAKE2s-16 digests. No K04 commitment hit; none equals the reconstructed PS-0417 ACK2 payload or its masked form.

Example: B,D,A,C XOR(rev1,rev2) vector = `7AC757F7F3A6BFD103DEBE18E239A918`; SHA-256 = `4979a330293d0d274f295e32a35961ec2b1adcf55e44ed8ca1c3a2f4e1381d7b`.

This only rejects the bounded revision-delta candidates, not every possible relationship between PTW-417 and the printer coupon. No broad PRNG/hash search was run.
