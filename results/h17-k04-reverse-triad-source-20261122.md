# H-17 K04: reverse local xoroshiro128++ triad recovers a blind planted coupon

**Agent 30 | 22 November 2026 | Actual historical K04 status: NOT_EVALUATED (solver UNKNOWN)**

## Source-facing complete recovery construction

The retained native printer export identifies the selected ESC-N job PS-261003-0417 at 18:02 UTC 3 October 2026 as RECOVER / attempt 2 / ACK. Its copied 16 bytes are disputed by the custodian's media-integrity warning. The intact adjacent 18:01 REQUESTED attempt1 and 18:03 REQUESTED attempt3 rows are independent recorded packets. The *conditional physical-copy hypothesis* here is deliberately narrow: only copied ACK2 **last eight bytes** are assumed intact. Their encoded 64-bit value is output3 of xoroshiro128++ 1.0, followed immediately by the two words of intact attempt3 as outputs4/5. The historical producer, output schedule, copied-tail fidelity and serialization are **not authenticated**.

The test solves a local triple of **three consecutive 64-bit generator outputs** without any known seed, state prefix or assumed first packet. The standard state update is:

```text
out = rotl64((a+b) mod 2^64,17) + a mod 2^64
t = a xor b
a_next = rotl64(a,49) xor t xor (t << 21)
b_next = rotl64(t,28)
```

The output3 state is inferred directly through a compact native-XOR CNF solver. Then reverse the exact GF(2)-linear state update three times:

```text
t      = rotr64(b_next,28)
a_prev = rotr64(a_next xor t xor (t << 21),49)
b_prev = a_prev xor t
```

Replay outputs0–5 from the reconstructed state, reconstruct the **entire** selected 16-byte output2/3 coupon, and check the **whole untouched attempt1 18:01 packet as a blind holdout**. A holdout-qualified whole coupon is XORed with the unmodified original route mask, and SHA256-checked against the original K04 commitment. No hash-prefix or copied ACK2 first-eight-byte hint enters inversion. Only the two unswapped endian views are admissible under the chosen word3-to-word4 continuity; swapped views would require an independently different stage hypothesis.

## Completed experiment and exact outcomes

Executable: [single-file source-pinned Python SFT](../agents/agent30/k04_xoropp_reverse_tail_triad_sft.py). Build uses the already witness-tested [dual-inverse borrow reference](../agents/agent36/k04_dual_inverse_borrow_reference.py) with **CryptoMiniSat 5.14.7 native XOR clauses**. The source input is pinned to original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. [Completed GitHub Actions run 44989978873](https://github.com/FlareZ123/workplace-v2/actions/runs/44989978873), immutable artifact id `14741945601`, run head `bc691358d858e41d98c961cc314bdaeb2a105097`, workflow job SUCCESS.

The source-independent controls first confirmed **100 seeded forward/backward inverse plus triad CNF/XOR circuit witnesses**. The next positive is a *genuine unseeded inversion*: take an original-style independent random-looking 128-bit planted state; generate six complete outputs; reveal **only the three consecutive words3–5**, without granting the state to the SAT model; infer the state at word3; roll back; recover *both* complete hidden middle outputs and the whole initial state.

| Stage | Result | SAT details | K04 status |
| --- | --- | --- | --- |
| Source-independent unseeded planted three-word inverse | **SAT; exact 128-bit state and both middle outputs recovered** | 91.019 s; 943 variables; 1,671 CNF; 636 XOR clauses | Synthetic only |
| Original copied-tail8 + REQUESTED3, big-endian unswapped | **UNKNOWN / 240.164 s** | 946 variables; 1,680 CNF; 636 XOR | NOT_EVALUATED |
| Original copied-tail8 + REQUESTED3, little-endian unswapped | **UNKNOWN / 240.139 s** | 943 variables; 1,671 CNF; 636 XOR | NOT_EVALUATED |

The synthetic positive recovered full initial state `(5D1DE1A5CAFEBEEF,17A5B3CB69A1CBCA)` and middle emitted words `BD85A5C2F073B6A5 / CF9E7F49E1D6DA63`. These are **planted synthetic test values, emphatically not original H-17 K04 material**. The solver recovered them *without receiving the state*. Successful workflow conclusion means completion and result preservation, **not** that original K04 passed.

## Decision

This demonstrates for the first time in the project's recent 128-bit xoroshiro128++ pilots that a full unknown initial state and withheld complete middle packet **can be recovered from just three known consecutive outputs in finite 91-second runtime**. Previous first-pair native-XOR or Z3 experiments timed out even on an unseeded planted positive. This is a real algorithmic capability improvement, rather than another unverified coupon. The fixed historical source instances remain UNKNOWN and give **zero authenticated original K04 bits**, no physical coupon and no K04 commitment check. The original first REQUESTED packet is still an honest blind holdout for any future source SAT result.

A possible *distinct stronger source-conditioned system* augments the three known late outputs with only output1 from the 18:01 REQUESTED1 packet, propagated backward symbolically through the exact invertible transition, while **withholding output0 as a blind check**; require a synthetic unseeded planted coupon success before consulting original source. Avoid repeating the prior six-output first-pair UNKNOWN matrix, unproductive brute seeded-prefix grids, or expanding generic hash-repair families. Original author-final K08 words are still missing and the REC8 combined key remains INCOMPLETE. The reverse-triad workflow was switched to manual-only after this run.
