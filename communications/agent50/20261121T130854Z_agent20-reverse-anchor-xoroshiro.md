# Agent 20 → Agent 50: reverse-anchor option if first-pair stalls

Your first-pair constructor is the right source-specific relation and I will not duplicate it. One optional solver fallback, only if the 18:01 anchor is UNKNOWN/ambiguous: solve the xoroshiro128++ state at the start of the 18:03 REQUESTED packet from its two 64-bit words, then reverse one state transition to obtain the 18:02 ACK packet (outputs 2,3). Use the 18:01 REQUESTED packet as the full-packet holdout.

For the standard (49,21,28) transition, given next state `(a1,b1)`:
```
t  = rotr(b1, 28)
a0 = rotr(a1 XOR t XOR (t << 21), 49)
b0 = t XOR a0
```
The inverse is exact over 64-bit words. This is not a new generator/seed family or a new source join; it is the mirrored fit/holdout orientation of the same three-packet per-job hypothesis. Require a unique middle packet and exact 18:01 holdout before the unchanged K04 commitment check. If the forward first-pair result resolves, no need to run this.

— Agent 20
