# K04: whole-packet 128-bit synchronization rotation with two arbitrary byte repairs

**Agent 3 | 9 November 2026 UTC | Complete original-target experiment, zero K04 matches.** The original six slots remain accepted; K04 and K08 unresolved, combined REC8/1 INCOMPLETE.

## Concrete recovery hypothesis

The selected original paper coupon is absent. The surviving printer export reports PS-261003-0417, RECOVER ACK attempt2 at 18:02Z, but ACK records dispatch and does not authenticate the copied 16-byte payload. To test a different capture fault from prior byte-only rotations or independent per-word rotations, model an original physical coupon as follows:

1. Rotate the entire **128-bit MSB-first** copied buffer circularly left by an integer number of bits, **0..127**.
2. Independently overwrite **at most two arbitrary byte positions** in that rotated packet with any octets.
3. XOR the resulting complete sixteen bytes with the unchanged original K04 route mask and compare **full SHA256** against the immutable acceptance commitment.

This is a speculative bitstream-desynchronization-plus-local-octet-fault model. The original export does **not** say its copying stage suffered a circular synchronization error or that exactly two bytes were corrupted. It is a complete-value hypothesis, not evidence that any selected original bit survived intact.

## Reproducible complete test

The [source-pinned C++17/OpenSSL single-file SFT](../agents/agent3/k04_128bitrotate_twobyte_sft.cpp) asserts original SHA256:

| Input | SHA256 |
|---|---|
| spool-reconstruction.log | 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083 |
| recovery-routing.json | f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5 |
| acceptance.json | 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f |

The SFT selects the one original printer line **2026-10-03T18:02:00Z / PS-261003-0417 / attempt2 / ACK / RECOVER** with copied payload **A9A9DC5731A5E2AE879C47215C2559D5**. The original K04 mask is **8556C8CB6140A7F9A5123AC7571BEE1C**, and the untouched full K04 commitment is **930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0**.

The enumerator visits all 128 rotations, all 120 pairs of distinct byte positions, and all 65,536 ordered two-byte values. It tests **1,006,632,960 complete SHA256(component) assignments**. Values include original octets, covering unchanged and one-byte-changed rotated packets too. Repetition across pair assignments is expected; the count is assignments, not unique coupons.

A synthetic complete physical coupon at rotation37 with byte5 = 3C and byte12 = D9 has its distinct synthetic masked-component digest computed independently and checked in the same enumeration. It was found once, validating the complete-value path without using the real K04 commitment to construct the positive.

Executed locally on the unchanged original ZIP extraction using Linux g++14, OpenSSL3.5.5 and eight OpenMP threads:

~~~text
SUMMARY rotations=128 position_pairs=120 each_values=65536 complete_assignments=1006632960 original_hits=0 planted_hits=1 seconds=149.318
~~~

Local executed SFT SHA256: **eb1c66798a269a687445b09e8ba0519d89ad73eb272750fc510b2557bf7af187**. The source was committed and the remote UTF-8 length/readback confirmed.

## Decision

**Zero** accepted K04 components lie in this specific entire-bitstream rotation followed by up-to-two-byte-repair family. Previous byte/nibble repairs, per-byte bitlane activation and independent 32-bit word rotation are complementary; the distinct operation here is a global 128-bit circular shift plus up to two unrestricted octets. No source proves this was the physical copy fault.

This does not exclude any physically different original coupon, more than two bad bytes, bit insertion/deletion with non-circular edges, or a different print producer. No authenticated selected original K04 bit was gained. K08's final authored caption remains unquoted. Original source files, route, verifier, acceptance and canonical candidate were untouched.
