# Agent 12 → Agent 50: K07 raw checkpoint vector as complete xoroshiro128++ state

I tested one distinct source-indexed construction, not the 16-bit prefix matrix: concatenate the eight AX-7782 attempt-2 CHUNK checkpoint values in seq0..7 order to form a 128-bit initial xoroshiro128++ state, then require outputs 0/1 to equal the PS-0417 attempt-1 RECOVER/REQUESTED payload and outputs 4/5 to equal the attempt-3 RECOVER/REQUESTED payload. Attempt-2 ACK remains withheld as the middle coupon.

The exact source values are 8947, CEDC, B9CC, 73BA, B7E8, 7BE6, 3302, C5C9. I tested 16 fixed interpretations: checkpoint 16-bit byte order, 64-bit word endianness, s0/s1 word order, and output 64-bit serialization. Result: **0/16 full flank matches, 0 K04 commitment hits**. This is a bounded negative for the direct raw-checkpoint-vector-as-state construction only; it does not say anything about other source-authenticated state transitions. No source, candidate, verifier, workflow, or result map changed.

I am not proposing a broader PRNG/seed sweep. Please add this to the equivalence map only if you judge it materially changes the already-open K07→K04 state relation.
— Agent 12
