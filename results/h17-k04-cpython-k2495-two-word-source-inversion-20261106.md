# H-17 K04: exhaustive genuine CPython two-word integer-seed exclusion at startup offset 2495

**Agent 1 | 6 November 2026 | Original-source conditional producer exclusion, zero physical selected-coupon bits recovered.** Six authentic slots remain PASS, K04/K08 remain MISSING, combined REC8/1 INCOMPLETE.

## A previously open early startup offset

The previous genuine CPython `init_by_array` inversion experiments have completely excluded the two-word key case at output offsets **2492, 2493 and 2494**, while the offset-2496 two-/three-word symbolic source attempts remain UNKNOWN. This experiment tests **true prior-output offset 2495**, without using the rejected physical/copy payload from PS-261003-0417 attempt2.

For the same **conditional** p951 fourword native-MT printer chronology, shift the previously independent selected-row-withheld source projection at offset2494 by one initialized register. The following are the original printer-source constraints at 2495:

| Initialized state | Mask | Required value | Fixed bits |
|---|---|---|---:|
| S4 | `8000001F` | `00000011` | 6 |
| S5 | `FFFFFFFF` | `E403BB7D` | 32 |
| S6 | `FFFFFFFF` | `1F7B301F` | 32 |
| S7 | `09CC1C00` | `008C1000` | 9 |
| S14 | `000000FF` | `000000B6` | 8 |
| S15 | `5398BA7D` | `4010A820` | 18 |

The input preserved printer spool `resources/evidence/print/spool-reconstruction.log` has SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, independently confirmed in the original attached ZIP this invocation. These observed mask constants are a **one-index shift of the already documented selected-withheld source projector**, not a separately re-fitted original physical value; the condition and chronology remain hypothetical. The source report for 2494 documents the preceding alignment: [k2494 genuine source](h17-k04-cpython-k2494-two-word-bitlift-complete-20261106.md).

## Different inversion: enumerate only the 23 missing source S7 bits

For genuine CPython two-word integer seeds `(k0,k1)`, use modulo-2^32 arithmetic. Let `G0=19650218`, `Gi=1812433253*(G(i-1) xor (G(i-1)>>30))+i`, `F1(x)=1664525*(x xor (x>>30))`, `F2(x)=1566083941*(x xor (x>>30))`, and `Ai` be the authentic `init_by_array` first-pass words before the second pass.

The two **fully determined original** initialized words `S5,S6` force `A6=(S6+6) xor F2(S5)`. This uses the genuine local second-pass identity for index6 and does **not** depend on the historically corrected first-pass index1 wrap approximation. The next pass gives

```text
A7 = (G7 xor F1(A6)) + k0
S7 = (A7 xor F2(S6)) - 7
k0 = ((S7+7) xor F2(S6)) - (G7 xor F1(A6))
```

Therefore **each** source-eligible full `S7` determines precisely one full `k0`. Exhaust all `2^23 = 8,388,608` values for the remaining 23 free S7 bits. No 32-bit k0 value satisfying the genuine source state is skipped.

For each derived k0, the exact first-pass `A6` equation determines k1 through the true (A1,A2,A3,A4,A5,A6) recurrence. Enumerate all four genuine high-two-bit patterns `h2=A2>>30`, `h3=A3>>30`, `h4=A4>>30`, `h5=A5>>30`, for **4^4 = 256** assignments. Freeze those high bits in each `F1(Ai)`, replacing `x xor (x>>30)` by `x xor hi`. The unknown k1's bit b enters A2 and A3 at b, cancels at A4/A5, and enters A6 at b exactly once. The map `k1 -> A6` consequently has odd low-bit derivative for *every frozen high-bit assignment*. Fix the **least mismatched bit** repeatedly, which finds the unique full 32-bit k1 for that high-bit pattern with at most 32 corrections; validate all four actual high-bit guesses against the full candidate A2..A5 before accepting it.

Every genuine fitting CPython two-word key must occur at one enumerated source-compatible S7, one of the 256 actual high-bit patterns, and its unique recovered k1. This is a completeness argument over the entire 64-bit integer-seed family **conditional on the specified source state**, rather than a 2^64 blind loop or an SMT timeout. Source S14/S15 masks are evaluated by forwarding exact `A7..A15`, `S7..S15`; if they both pass, the reproducer additionally recalculates all 624 authentic `init_by_array` state words to test the earlier S4/S5/S6 observations.

## Executed exhaustive original run

[Standalone C++17 original-domain SFT](../agents/agent1/k04_cpython_k2495_n2_inverse_sft.cpp) is 6,650 bytes and source-identical to the local executed version (local SHA256 `3e87e96fa48a05c1d8ec8216f57f91496242d90c3f5f7c9f7b115c0956780c5e`). It was compiled with an optimizing C++17 compiler and run across **32 disjoint contiguous 262,144-S7 windows** covering `[0,8388608)` exactly once. Each individual shard reports its start/count, 256 highbit paths per S7 value, accepted genuine highbit roots, S14 survivors, S15 survivors, and complete original-state survivors. The underlying original evidence, original verifier, original commitments, and canonical candidate were not modified.

| Source S7 window (eight shards) | S7 inputs | Frozen hi-bit paths | Real hi-bit roots | After S14 8-bit mask | After S15 18-bit mask |
|---|---:|---:|---:|---:|---:|
| 0..2,097,151 | 2,097,152 | 536,870,912 | 2,097,228 | 8,157 | **0** |
| 2,097,152..4,194,303 | 2,097,152 | 536,870,912 | 2,098,053 | 8,231 | **0** |
| 4,194,304..6,291,455 | 2,097,152 | 536,870,912 | 2,095,530 | 8,231 | **0** |
| 6,291,456..8,388,607 | 2,097,152 | 536,870,912 | 2,096,911 | 8,335 | **0** |
| **Complete** | **8,388,608** | **2,147,483,648** | **8,387,722** | **32,954** | **0** |

**Independent genuine Python controls:** separately calculate `random.Random((k1<<32)|k0).getstate()` fixture words S4,S5,S6,S7,S14,S15,S100,S623 for each seed `(12345678,23456789)`, `(00001FC3,00001092)`, `(FFFFFFFF,FFFFFFFF)`, `(00000000,80000000)`, `(80000000,00000001)`. Each of the five seeded fixtures matches the C++ **full 624-register** initializer at all eight checked indices. The source S7 value reconstructs its actual k0 and the unique frozen-highbit inverse recovers the exact k1, with its complete original-like S4/S5/S6/S14/S15 checking gate. **Five of five complete planted positives passed.**

The original zero at S15 is decisive for this conditional exact seed family; no earlier-state false negatives can be caused by post-filtering because no full original input survives the necessary source masks.

## Consequence

**New finite exclusion:** the p951 native spool chronology **cannot** have been produced by a genuine CPython MT19937 `random.Random` **two-word integer seed at true output offset 2495**, given the inherited selected-withheld printer source-state projection. Together with separately completed 2492/2493/2494 studies, this closes four adjacent n2 offsets. This result says nothing definitive about a 2496 seed, longer seed arrays, a different printer emitter, selected-only rekeying, or the true physical attempt-2 coupon. It does not recover any of the original K04 128 selected bits. K08's exact author-final words are also unavailable.

The reusable method is **low-missing-bit source enumeration coupled to a unique triangular 32-bit key inversion**, with a complete genuine seeded control and independent later source mask. Future work should seek a producer with selected-object predictive evidence instead of automatically extending more artificial offsets.