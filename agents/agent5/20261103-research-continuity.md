# Agent 5 current research continuity, 3 November 2026

**Current incarnation:** normal mode from an executed `secrets.randbelow(10)+1` draw of **7**. Claimed the free Agent 5 identity by remotely committed/verified lease at **2026-11-03T03:17:02.106712Z**, immutable `run_id=7ad2b7bc-4c16-4ff3-a4cd-d22cacabcbd5`. This file supplements the large pre-existing [memory.md](memory.md), whose prior incarnation claimed at 01:56 UTC and correctly released near 03:07 UTC. After each checkpoint use the original **03:17:02 UTC** lease timestamp for the mandatory 70-minute decision; only release when clock >= **04:27:02 UTC**.

Active README and 2 Nov maintainer override: six of eight historical REC8/1 slots remain accepted, K04/K08 unresolved. The target is intact archive recovery, not facility operation. Do not redo six-slot verification or reuse massive failed v1 combinatorial loops.

## Novel direct-source PRNG model tests

Durable source-only SFTs and top-level findings:

- [xoshiro128**, xoroshiro128**, xoshiro256** inversion](k04_nonmt_direct_stream_sft.py), [original-source result](../../results/h17-k04-nonmt-direct-output-producer-control.md): 60 seeded complete-state recovery controls pass. Original routine next-packet holdouts fail 0/508, 0/508, 0/504 respectively; 128-bit model state-to-next-state hidden gap 0..4096 fails 0/1016 original adjacent source/layout/model cases, planted gap controls pass.
- [Java Random 48-bit LCG state inversion](k04_java_random48_sft.py), appended in above result: 100 seeded controls pass; 0/128 original routine ACK first-pair possibilities in all four 32-bit word layouts, before considering the full four-word packet.
- [PCG-XSH-RR 64/32, arbitrary increment, exact lattice inversion](k04_pcg32_unknown_increment_lattice_sft.py), [full evidence and mathematics](../../results/h17-k04-pcg32-unknowninc-lattice-source-falsifier.md). 3 separate planted 64-bit state/increment controls pass after exhaustive 32^4 output-rotation scan. 0 valid four-word PCG models across four separated intact printer packets × four native endian/order layouts. This is a stronger **per-packet arbitrary-seed and arbitrary-increment** negative; the 3D affine lattice certificate with nearest-integer error strictly <1/2 makes the inversion exhaustive under the tested four-consecutive-native-output model. The result does not exclude nonconsecutive draws or transformed serialized output.
- Source input is the 128 routine 5-minute ACKs from `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Disputed selected 18:02 attempt-2 ACK never contributes to model fitting; original K04 commitment never used.
- Important PCG caveat: although the unknown 64-bit state plus 64-bit increment nominally span 128 bits, output mapping has large low-state parameter collisions: each recovered rotation tuple can admit millions of initial low bits and adjusted increment. Thus a random 128-bit four-output packet is usually unrepresentable; 9 randomly generated four-word packets had 0 recovery fits in a preliminary calibration. The zero-hits are substantive model exclusions, but could not recover selected bytes.

**No authenticated K04 target bit and no verbatim K08 final caption word.** All official evidence and commitments remain unmodified.

## Next attack

Test source-plausible **regularly skipped PCG native draws** with stride 2..N, whose effective multiplier is `6364136223846793005^stride mod 2^64` and whose increment remains arbitrary. Recompute 3D lattice basis/inverse for each stride using an exact integer-reduced lattice and certify the rounding error before testing intact source. This would cover interleaved draws/generator calls that the direct-consecutive model excluded. Preserve seeded controls and report any source fit with a separately withheld intact check, not retrospective matching alone.

Parallel unresolved avenues: source-labelled print capture transformation with a selected-event bridge, or an actually author-grounded K08 version/custody operation. Avoid larger unconstrained phrase sweeps.
