# K04 exact-state inversion of six fast PRNG producers (3 November 2026, Agent 9)

**Outcome: zero exact source-family fits.** This is a newly implemented source-producer discrimination test; it does **not** derive an authentic selected coupon, its mask, or any K04 component bits. K04 and K08 remain unresolved, with combined REC8/1 acceptance INCOMPLETE.

## Recovery hypothesis

The 128 regular one-attempt, five-minute printer rows, jobs PS-261003-0300 through -0427, may be contiguous serializations of output from a compact-state fast PRNG. Unlike seed-name brute force, the three **-starstar generators have invertible multiplication-and-rotation output scramblers**. A full emitted 32/64-bit word reveals the corresponding internal GF(2)-linear state word. With a fixed producer transition, a handful of complete 16-byte packets can therefore determine the state algebraically and predict the rest of the stream. The three Marsaglia xorshift controls directly expose their GF(2)-linear generator output.

Six possible producers were tested with their standard transitions:

1. xoshiro256** (256-bit state, 64-bit words)
2. xoshiro128** version 1.1 (128-bit state, 32-bit words)
3. xoroshiro128** (128-bit state, 64-bit words)
4. Marsaglia xorshift128 with 11/8/19 shifts (128-bit state, 32-bit words)
5. Marsaglia xorshift32 with 13/17/5 shifts
6. Marsaglia xorshift64 with 13/7/17 shifts.

Each model received two per-word endian orders, forward/reversed word order within a 16-byte coupon, and constant skipped-output counts **0, 1, 2, 3, 4, 8, 16, 32** at each packet boundary. This yields **192 complete configurations**. For each configuration the first six *ordinary* spool buffers provide up to 24 direct state-word observations. The remainder of the original 128 regular buffers are withheld for complete-byte validation. The exceptional 0417 ACK2 at 18:02 UTC is excluded from both fitting and controls.

## Reproduction and source constraints

- [Exact executable SFT](../agents/agent9/k04_linear_prng_family_sft.py); Python standard library, from repository root: `python agents/agent9/k04_linear_prng_family_sft.py`.
- Source: `resources/evidence/print/spool-reconstruction.log`; pinned SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- The SFT applies bitwise GF(2) Gaussian elimination and reconstructs the original full state only when determined. It then predicts whole serialized source packets with the real PRNG transition and output function.
- Six constructed synthetic streams, one for each model and including endian, order, gap variations, were fully reconstructed and predicted **12/12** packets. These synthetic positive controls are explicitly separate from historical records.
- On original source, **192 configurations**, of which **181** reached full GF(2) state rank before an observational contradiction; **zero** fit. No complete 128-row prediction, selected coupon, or K04 commitment PASS resulted.

Reference transition definitions: [Blackman/Vigna original xoshiro family](https://prng.di.unimi.it/) and [xoshiro128**](https://prng.di.unimi.it/xoshiro128starstar.c), [xoroshiro128**](https://prng.di.unimi.it/xoroshiro128starstar.c). The Marsaglia recurrence follows the published xorshift variants. No evidence currently establishes any of these as historical printer firmware.

## What this actually excludes

The negative result excludes exactly the 192 **single persistent state, full-width output, constant interpacket skip** models above for the original regular-spool observations. The observed regular spool may instead use a different producer, variable per-row draws, per-job reseeding, truncated generator output, a keyed cipher, or unrelated entropy. No claim is made that a producer surviving a test would authenticate the disputed selected physical ACK2 stage. In particular, ordinary one-ACK rows are not matched retries. This is a scoped algebraic producer test rather than a blanket denial of recoverability.

The strongest follow-up would acquire an end-to-end producer mechanism that also predicts the distinct retry-class comparator `PS-261003-0420` ACK2 with its output withheld, then freezes an interpretation of the selected 0417 ACK2. More raw fast-PRNG name enumeration without such a bridge has low priority.