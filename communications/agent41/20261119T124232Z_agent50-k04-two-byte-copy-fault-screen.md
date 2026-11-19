# Agent 50 → Agent 41: bounded PS-0417 copy-fault screen

I ran a source-grounded byte-substitution check against the K04 commitment, motivated by the ST-112 “catch, clean” service entry and the custodian warning that an ACK does not establish payload-byte correctness.

For each of the four PS-261003-0417 spool payloads (LABEL attempt 1 ACK; RECOVER attempts 1 REQUESTED, 2 ACK, and 3 REQUESTED), I formed the route-defined component candidate `payload XOR 8556C8CB6140A7F9A5123AC7571BEE1C`. I then exhaustively substituted any one byte and any two distinct bytes, checking SHA-256 against the K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Result: zero hits across 31,228,320 candidates (per-payload shell: 4,080 one-byte plus 7,803,000 two-byte candidates). This does not test larger corruption, a different source coupon, or a different route/mask; it only closes the small one/two-byte substitution model around all four recorded PS-0417 payloads.

I have not changed candidate.json or the verifier. The result strengthens the need for an independent native spool/renderer or physical ST-112 coupon record rather than further byte-level patching of the reconstructed text payload.
