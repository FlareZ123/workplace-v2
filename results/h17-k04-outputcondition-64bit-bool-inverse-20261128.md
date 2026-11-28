# K04 producer research — output-conditioned 64-variable Boolean xoroshiro128++ inversion

**Agent 5 · 28 November 2026 · synthetic mathematical method, no historical component recovered.**

## Distinct calculation

For xoroshiro128++ 1.0, write `a,b` for its first two 64-bit state words, `t=a XOR b`, and observe the output
`y=ROTL64(a+b,17)+a (mod 2^64)`. Every possible initial `a` has **exactly one** corresponding `b = ROTR64(y-a,17)-a`. Thus one observed output permits an exact 64-bit, rather than 128-bit, state coordinate. This basic reduction is equivalent to the earlier sum-coordinate parameterization, not an independent entropy leak.

The incremental implementation is a **purely Boolean, output-conditioned carry** circuit that computes `t` from the 64 Boolean bits of `a` and the known bits of `y`, with no symbolic 64-bit adder/subtractor. Let `u[k]` be the carry into bit k of `a+b`, and `v[j]` that of `ROTL(a+b,17)+a`, with `u[0]=v[0]=0`. Then

```
v[j+1] = (a[j] AND v[j]) if y[j] = 1
         (a[j] OR  v[j]) if y[j] = 0
j       = (k+17) mod 64
t[k]    = y[j] XOR a[j] XOR v[j] XOR u[k]
u[k+1] = u[k] if t[k] = 1 else a[k]
```

The second carry recurrence is an identity of binary full-adder majority under known output parity; the first is the majority simplification for `b=a XOR t`. Since the `v` values depend only on the chosen `a`, and `u[k]` is determined from earlier k, this computes all 64 `t` bits without search or loops. At the next observed output, the genuine linear xoroshiro transition gives the candidate `(a',t')`; assert `t' = T_y(a')` for each of the 64 bits. Erased outputs advance the linear state without an output equation. This leaves **exactly 64 independent Boolean primary state variables**, versus the earlier separate 82-primary-bit `(t,a-low17,carry)` circuit. It does **not** prove easier generic inversion.

## Fully synthetic controls

[Source-free reproducible solver](../agents/agent5/k04_xoropp_output_conditioned_bool_synthetic.py) uses `libz3.so.4` through `ctypes`, contains no archive literals or target materials, and independently replays the full sequence before returning a model.

- **10,000** pseudorandom `(a,y)` cases verify `T_y(a)` against the exact closed-form inverse and original forward generator.
- On seed **20261128**, two successive unanchored, *four-consecutive-output* planted cases recovered the entire initial 128-bit state exactly, in **60.474** and **76.172** seconds with a 90,000 ms per-case limit. These are source-free controls, not a printer fit.
- The same first planted source, with only *two consecutive outputs*, returned **UNKNOWN** at **90.027** seconds; an erased middle pair with visible positions 0,1,4,5 returned **UNKNOWN** at **90.008** seconds. UNKNOWN is neither impossible nor a certificate of uniqueness.
- A correct synthetic **16-bit low-a anchor** under two consecutive outputs returned exact SAT in **0.122** seconds, but wrong 16-bit anchors sometimes required multiple seconds or timed out. This is not a feasible exhaustive 16-bit-anchor search and supplies no source-authenticated initial-state bits.

The important frontier is recovery of an **entire 16-byte erased middle packet** from only the surrounding original REQUESTED records; the plant has not yet passed that gate under this encoding. A useful separate variant would treat only one *independently warranted* half of a copied middle packet as intact, predict the entire other half, and replay both untouched outer packets. Do not assume the historical copied ACK is itself the physical coupon: directly reusing it has already failed the original K04 commitment.

## Boundary

This is an alternative Boolean exact-reduction strategy, **not** an authenticated printer producer, proof of physical coupon copying, or K04 recovery. The actual historical xoroshiro family and consecutive draw schedule remain conjectural, and no result here derives a historical component. No source-bearing public CI was dispatched, and no original archive, acceptance, verifier, canonical candidate, quarantined PDF, source payload bytes or generated sensitive diagnostics was altered or published. Six components previously accepted remain accepted; K04/K08 and combined REC8/1 remain unresolved.
