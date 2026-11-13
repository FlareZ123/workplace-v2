# H-17 K04: official TinyMT64 127-bit source-consistency inverse

**Agent 3 | 13 November 2026 | 36 fully specified original-source models, 0 consistent.**

## New producer question

Could the ordinary printer's opaque 16-byte buffers be consecutive pairs of the standard **64-bit Tiny Mersenne Twister** outputs, possibly with a fixed number of unseen 64-bit words between jobs? This is a distinct 127-bit state-transition model from the previously tested TinyMT32, native MT19937, Xorshift1024, and large-state conditional p951 donor variants.

TinyMT64's reference parameters are `mat1=FA051F40`, `mat2=FFD0FFF4`, `tmat=58D02FFEFFBFFFBC`, from the MersenneTwister-Lab TinyMT reference implementation. With this standard `tmat`, the least significant bit of each 64-bit output is exactly an F2-linear observation of the 127-bit state, even though the complete output tempering contains addition with carries. This allows a cheap complete source **falsification before inversion of full-output bytes**.

The 128 ordinary 07:00–17:35 printer rows are the intact source observations. The selected PS-261003-0417 ACK attempt 2 and all four later special records remain excluded from state fitting.

## Frozen model and experiment

Original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

For each ordinary 16-byte packet, read two consecutive 64-bit generator outputs. Cross 9 fixed inter-packet gaps (0..8 unprinted 64-bit outputs) with original/reversed half order and little/big-endian 64-bit serialization. This yields **36 complete source-producer assignments**. Freeze every assignment before comparing the source.

Generate each output-bit equation by running each of the 128 unit basis states through the official state transition. Perform exact GF(2) elimination on the first 80 whole packets (160 output-low-bit equations). Only a fully consistent original-source producer would be eligible to reconstruct later complete outputs, validate the late whole-packet controls, and attempt K04 reduction.

**Original result:** all 36 models are inconsistent by output-bit equation 126–131, after source-basis ranks 125–127. **Zero models survive the first 80 original packets.** No late whole-object prediction or K04 commitment check is source-qualified; no K04 candidate was obtained.

The script checks the original authors' seed-1 first six 64-bit outputs exactly. Three planted complete 128-packet streams with gaps 0, 3, 8 and varied serializers each permit recovery of the unknown 127-bit state from the first 80 packets, followed by exact reproduction of the **48 previously unseen entire 16-byte packets**. This verifies the producer inverse, serializer, low-bit projection and full-byte blind forecast under real positive models.

## Boundary

This falsifies the standard-parameter TinyMT64 constant-gap model for the 128 retained ordinary printers, with the exact stated serializers and 0..8 fixed inter-packet gaps. A different parameter polynomial, nonconstant source call schedule, separate producer per job, damaged ordinary source bytes, or unrelated issuer remains outside the test. No source attests that the historical printer used TinyMT64. The result adds no authenticated selected-coupon bits, and **must not** be extended into arbitrary parameter/gap sweeps without a historical selection cue.

Portable reproducer: [Agent3 TinyMT64 source inverse](../agents/agent3/k04_tinymt64_lowbit_source_sft.py). Authoritative algorithm: [TinyMT64 header](https://github.com/MersenneTwister-Lab/TinyMT/blob/master/tinymt/tinymt64.h) and [official check64 output](https://github.com/MersenneTwister-Lab/TinyMT/blob/master/tinymt/check64.out.txt).

The untouched official REC8/1 state remains **six PASS; K04 and K08 MISSING; combined INCOMPLETE**. No source file, route, acceptance, verifier or canonical candidate was changed.
