# PTW-417 raw-quartet alternative PRNG candidate screen

**Date:** 2026-11-25

## Question

Can the highest signed `CLOSED / AS_LEFT` PTW-417 serial for each bay, interpreted as a 128-bit PRNG state or seed, produce a K04 component that passes the original slot commitment after the prescribed XOR mask?

## Method

- Used the four PTW-417 selected bay serials as a raw 128-bit state/seed; no PS-0417 payload bytes were used as seed material.
- Tested both bay orders already present in the source research.
- Tested xoshiro128** / xoshiro128++, xoroshiro128++ / xoroshiro128**, xorshift128+, Python MT19937 and NumPy PCG64 / PCG64DXSM.
- Varied 4×32-bit and 2×64-bit state layouts, applicable byte/word endianness and word order, and bounded warm-up offsets (0–64 for xoshiro/xoroshiro/xorshift; 0–32 for MT/PCG).
- For each generated 16-byte output, applied the unchanged K04 XOR mask and compared SHA-256 against the K04 slot commitment. The selected PS-0417 ACK2 payload was used only as a separate exact-output comparison control.
- Synthetic xoshiro reference checks passed. NumPy version: 2.3.5.
- Reproducer: `work/h17_k04_ptw417_alt_prng_candidate_screen.py`. It prints aggregate/configuration results only; any candidate output is written locally only when an explicit output path is supplied.

## Result

**No K04 commitment hits.**

- 16,408 parameter configurations tested.
- K04 commitment hits: **0**.
- Exact output matches to the selected ACK2 payload: **0**.
- No candidate component was emitted.

## Interpretation and limits

This closes only the listed raw-quartet PRNG/state constructors and bounded warm-up ranges. It does not prove that every possible producer or source relationship is impossible. In particular, the PTW-417 / PS-0417 same-suffix relationship remains unauthenticated; this screen is exploratory, not historical evidence.

Do not widen this family without a source-authenticated PTW→printer join or a materially different producer rule. The K04 blocker remains the independently authenticated physical ESC-N coupon or a native PS-0417 attempt-2 job plus device/media-integrity witness.
