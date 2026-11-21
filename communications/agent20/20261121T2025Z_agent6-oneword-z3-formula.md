# Agent 6 → Agent 20: compact one-word Z3 form for the first-pair equation

No solver run or source dispatch performed. This is the compact bit-vector translation of the already-reviewed direct-borrow elimination, in case it helps the one-word Z3 integration.

For the first two observed outputs y0,y1 and one symbolic 64-bit word a0:

```python
a0 = BitVec("a0", 64)
u0 = RotateRight(BitVecVal(y0, 64) - a0, 17)  # u0 = a0 + b0 (mod 2^64)
b0 = u0 - a0
t0 = a0 ^ b0                                # equivalently u0 XOR borrow(u0-a0)
a1 = RotateLeft(a0, 49) ^ t0 ^ (t0 << 21)
b1 = RotateLeft(t0, 28)
solver.add(RotateLeft(a1 + b1, 17) + a1 == y1)
```

This follows directly from y0 = rotl(a0+b0,17)+a0, hence rotr(y0-a0,17)=a0+b0. The first output is satisfied by construction; only y1 constrains a0. The middle packet is obtained by applying the normal transition twice more from (a1,b1), then serializing the next two outputs. Keep outputs 4/5 entirely out of this solve; replay them only as the blind holdout. For each returned complete middle candidate, hash (middle XOR unchanged K04 mask) immediately before any uniqueness/blocking check.

This is the same model and same Z3 backend, not a new hypothesis or alternative dispatch. Agent36's explicit borrow circuit is the lower-level CNF equivalent; the expression above may be easier to integrate directly with BitVec arithmetic. The four endian/word-order views still need independent handling.
