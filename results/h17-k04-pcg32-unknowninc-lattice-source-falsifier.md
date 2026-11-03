# K04: exact PCG32 unknown-increment packet-state inversion against original printer controls

**Agent 5 | 3 November 2026 | Source-only, model-restricted negative.**

## Question

Can a routine 16-byte ACK packet be the four consecutive full native 32-bit outputs of a PCG-XSH-RR 64/32 pseudorandom generator? This hypothesis is materially different from the widely studied conditional MT19937 producer, and even allows a **different arbitrary 64-bit state and arbitrary 64-bit increment for every packet**. A successful construction could have produced complete testable missing-coupon candidates once a source-backed selected-job state/copy rule was identified.

## Exact inversion, without brute-forcing a 64-bit seed

The tested PCG-XSH-RR output operation for 64-bit state `s` is

```text
rotate_right_32((((s >> 18) XOR s) >> 27) & 0xffffffff, s >> 59).
```

The state advances as `s_next = 6364136223846793005*s + inc (mod 2^64)`, for unknown `inc`. With one observed 32-bit word and a 5-bit guessed rotation, the output formula determines the **top 37 state bits uniquely**, leaving 27 low unknown bits.

For a four-word packet, enumerate all `32^4 = 1,048,576` rotation tuples. Each tuple gives four 37-bit state prefixes `h0..h3`. Write the states as `si = 2^27*hi + li` where `0 <= li < 2^27`. Eliminating the arbitrary constant increment gives two exact modular second-difference equations on low-state differences `d1=l1-l0`, `d2=l2-l0`, `d3=l3-l0`.

The resulting three-dimensional affine integer lattice has a precomputed, explicitly pinned exact basis `R` and inverse `N/2^64`. The reproducer asserts the identity `R*N = 2^64 I`, both homogeneous recurrence equations for every basis row, and a strict nearest-integer certificate: for every coordinate, the error induced by any legitimate low-state difference is bounded by

```text
2^27 * sum(abs(column entries of N)) / 2^64 < 1/2.
```

Thus one nearest-integer rounding per rotation tuple recovers the **unique possible integral low-state differences** in the bounded box, with **no heuristic search radius, missed candidates, or presumption about the increment**. It then checks that four recovered states admit the *same* increment and reproduce every observed PCG output. This is an exhaustive inversion of this complete-packet model. The code handles the interval of possible initial low bits when more than one represents the same four states.

## Reproducible experiment

[Read-only standalone Python SFT](../agents/agent5/k04_pcg32_unknown_increment_lattice_sft.py), standard library only. It pins `resources/evidence/print/spool-reconstruction.log` to SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, selects four widely separated **original intact ordinary** first-attempt ACK rows `0,43,84,127` and excludes the selected disputed `PS-261003-0417` attempt-2 payload and special-tail jobs completely. Each original row is tested in four plausible native output layouts: little/big-endian 32-bit words with forward/reversed word ordering.

Before examining original rows, **3/3 independently seeded random 64-bit-state / odd-64-bit-increment synthetic controls** were recovered under exhaustive one-million-rotation inversion, including matching the true rotation tuple. Their planted increments are different.

| Original intact row | Four layouts | Complete PCG32 four-output fits |
|---|---:|---:|
| 0 | 4 | 0 |
| 43 | 4 | 0 |
| 84 | 4 | 0 |
| 127 | 4 | 0 |
| **Total** | **16 million-rotation scans** | **0** |

No canonical K04 candidate, K04 commitment hash, or verifier was used in this producer screen.

## Interpretation and next test

This excludes the precisely specified **four consecutive native PCG-XSH-RR outputs per packet** under all four tested serialization layouts, despite allowing unrestricted per-packet seeds and unrestricted per-packet increments, with exhaustive internal-state search rather than a sample of candidate seeds. By itself it cannot reject nonconsecutive samples, a per-word transform, truncated/woven outputs, different PCG output permutations, buffered/copy-stage transformations, or another PRNG.

The loss-making assumption is the **mapping between 16 serialized packet bytes and four consecutive native generator outputs**. Any follow-up PCG attempt should state and derive a different source-meaningful layout or capture rule, and predict an intact withheld packet before claiming progress toward the selected coupon.

**Recovery status:** no authenticated selected K04 bit, no author-final K08 word. Existing six accepted slots and their commitments are unchanged; combined acceptance remains incomplete.
