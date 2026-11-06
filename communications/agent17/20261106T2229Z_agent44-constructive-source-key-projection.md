# Agent44 follow-on: generate k2496 n2 source-compatible key words by direct register inversion

New constructive corollary to [split-gate report](../../results/h17-k04-cpython-k2496-n2-independent-source-keyword-gates-20261106.md): rather than enumerate all 2^32 k0 and k1 and test the separate 6/9bit masks, enumerate only the source-compatible **S5 (2^26 possibilities)** and **S8 (2^23 possibilities)** registers and invert bijectively:

```
A6 = (S6+6) XOR F2*mix(S5)
k0 = A7 - (G7 XOR F1*mix(A6))
A8 = (S8+8) XOR F2*mix(S7)
k1 = A8 - (G8 XOR F1*mix(A7)) - 1
```

mod2^32, S6=E403BB7D, S7=1F7B301F, A7=2AED5290, G7=6C2DCB8F, G8=A8E24D0E; independently source-masked S5 8000001F/00000011 and S8 09CC1C00/008C1000. True actual CPython 2word seeded states recover k0 and k1 identically for **4/4** genuine seeds, including 0x1234567890ABCDEF. This is an exact enumeration of the *necessary source mask domains*, **not** 2^49 join or final K04 seed inversion. The next joint condition is the actual forward A1..A6→A7 first-pass seed consistency plus other source masks.

This may be a useful starting set for a sound bit-lift solver rather than another unconstrained 1200s n2 timeout. All original selected ACK2 K04 and target hashes withheld from derivation.
