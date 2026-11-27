# K04 — exact xoroshiro128++ sum-coordinate reduction and PTW anchor screen

**Agent 31 · 27 Nov 2026 · original-source conditional negative, not recovery.** The existing six REC8/1 slots remain accepted; K04 and K08 unresolved. No original coupon component was produced.

## Mathematical construction (new coordinate, unchanged generator)

For one xoroshiro128++ state `(a,b)`, define `c=(a+b) mod 2^64`. Its first output is
`y0 = rotl64(c,17)+a (mod 2^64)`. Therefore
`a=y0-rotl64(c,17)`, `b=c-a` (all modulo `2^64`).
Once `y0` is observed, **one 64-bit word c determines the entire 128-bit state exactly**. Substitute these expressions into the official transition:

```text
t    = a xor b
a1   = rotl64(a,49) xor t xor (t << 21)
b1   = rotl64(t,28)
y1   = rotl64(a1+b1,17)+a1
```

The sole remaining unknown is `c`, subject to the exact second-output equation `y1(c)=observed_y1`. This is an exact reparameterization, *not* a polynomial-time inverse or evidence that xoroshiro generated the source.

## Reproducibility and test

[Synthetic-only QF_BV solver](../agents/agent31/k04_xoropp_sumstate_qfbv_synthetic.py) uses installed `libz3.so.4` via Python ctypes, with no historical literals, target or protected files. Planted controls use fixed pseudorandom seed **20261127**: 16/16 correctly anchored low-32 sum-state fixtures yielded exact SAT and 16/16 wrong-anchor controls yielded exact UNSAT. A 32-bit correct anchor on a separate seed **1847** yielded SAT in 0.027 s; with no anchor the exact 64-bit equation returned UNKNOWN at 5 and 25 s. Adding a synthetic four- or eight-output stream likewise timed out at 10 and 20 s. **UNKNOWN does not imply UNSAT**. These measurements are local, environment-dependent and make no claim of a fast general inversion.

The separate [offline source screen](../agents/agent31/k04_xoropp_ptw_sumanchor_source_screen.py) pins the original seal-receipt and printer-source hashes, selects each of the four highest signed CLOSED AS_LEFT PTW-417 bay serials, and uses only the intact PS-0417 ATTEMPT=1 REQUESTED packet as a *hypothetical* consecutive two-output witness. It tests 4 bays × 2 serial-endian readings × 2 placements (low/high 32 bits of c) × 2 packet endiannesses × 2 64-bit half orders = **64 complete sum-state anchor configurations**. All 64 were **UNSAT** in the local QF_BV reduction, each within 0.27 s under a 3.5-s per-configuration limit. The selected ACK2, physical coupon, K04 target digest, PDF and K08 material were not read by this program. No public source-bearing CI ran.

## Interpretation

This excludes exactly the proposed PTW-417 serial-as-32-bits-of-*sum state* construction under the retained REQUESTED1 consecutive-output and four packet-view hypotheses. Agent12's 27 November half-state inversion instead fixes `b` and is logically different: this screen constrains `a+b`. Neither construction authenticates any PTW→printer generator link. It produces **zero K04 commitment hits because it produces no original candidate**; do not misreport an empty search as coupon recovery.

Further progress from this coordinate requires a source-authenticated or sharply source-selected observation of at least part of the generator's pre-scrambler sum `c`, or a genuinely faster generic two-output inversion. Repeating arbitrary 32-bit donors without such a relation is not a justified next move.
