# Rolling PTW alternative PRNG / warm-up screen

**Date:** 2026-11-25  
**Scope:** bounded, target-blind extension of the existing rolling-PTW → xoroshiro128++ experiment. This is exploratory and does not authenticate a PTW→printer join.

## Question

Can the rolling four-bay PTW state that was previously tested as a fixed xoroshiro128++ state reproduce the intact same-suffix printer packets under other plausible 128-bit PRNG families or a bounded warm-up offset?

## Method

- Reused the existing loader in `resources/work/test_rolling_ptw_xoroshiro128pp.py`.
- Built each training state by retaining the latest signed `CLOSED / AS_LEFT` four-byte serial for each bay while processing PTW-390 through PTW-416.
- Compared the resulting rolling state after each permit with the one retained ACK packet for the same-suffix PS-0395 through PS-0416 jobs (22 training pairs).
- PS-0417 was excluded from fitting and no target candidate was emitted.
- Tested:
  - Four 32-bit state words: xoshiro128** and xoshiro128++, both declared bay orders, big/little word interpretation, warm-up offsets 0–64, both output byte orders and word orders.
  - Two 64-bit state words: xoroshiro128++, xoroshiro128**, and xorshift128+, both bay orders, per-serial and state-word endianness, state-word swap, warm-up offsets 0–64, both output byte orders and word orders.
  - 128-bit rolling-block seeds: Python MT19937 (four 32-bit outputs or one 128-bit output) and NumPy PCG64 / PCG64DXSM, warm-up offsets 0–32, with applicable output serializers. NumPy version: 2.3.5.
- Synthetic known-answer checks passed for xoshiro128** / xoshiro128++ reference states and for the xoroshiro128++ implementation against the existing baseline implementation.
- Reproducer: `work/h17_k04_rolling_ptw_alt_prng_warmup.py`.

## Result

**Result: no exact matches.**

- 16,408 parameter configurations tested.
- Maximum exact packet matches: **0 of 22**.
- All 16,408 configurations produced zero exact matches.
- No PS-0417 payload or K04 component was generated.

## Interpretation and limits

This closes only the listed rolling-state PRNG constructors and bounded warm-up ranges. It does **not** prove that every PRNG, seed construction, byte transform, or PTW/printer relationship is impossible. The same-suffix PTW/PS association remains exploratory and unauthenticated; the result is not evidence that PTW serials generated the printer payloads.

Do not widen this family without a source-authenticated PTW→printer join or a materially different producer rule. The unresolved K04 blocker remains independent media/source integrity for PS-0417 ACK2: the retained ACK is dispatch evidence, not proof of the rendered coupon bytes. A native attempt-2 queue/journal, complete driver-level job object and media-integrity witness, or the original ESC-N coupon/bench handoff is still required.
