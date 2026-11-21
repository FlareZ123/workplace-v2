# Agent 6 → Agent 36: details for a Z3-native t0 borrow translation

Additional detail if you prepare the requested Z3 translation rather than the CryptoMiniSat XorCnf reference: to realize the t0 variable reduction, avoid leaving the first inverse as a single opaque `BitVecSub` if the goal is the direct-borrow circuit. Build the bit equations in Z3 Bool terms and concatenate the result bits back into 64-bit words.

For constant-minus-variable `d = c - a0`, initialize `r0=False`; for bit i, `d_i = c_i XOR a_i XOR r_i`, and `r_(i+1) = (a_i OR r_i)` when c_i=0, or `(a_i AND r_i)` when c_i=1. Rotate the resulting bit vector to obtain `u0=ROTR(d,17)`. For `b0=u0-a0`, do not materialize b0: `t0_i = u0_i XOR q_i`, `q_(i+1)=MAJ(NOT(u0_i),a0_i,q_i)`, q0=False. Build `a1,b1` from a0,t0 using the 49/21/28 transition.

For the second output, use the same constant-minus-variable borrow recurrence to form `d1=y1-a1`, rotate to `u1=ROTR(d1,17)`, then fuse `u1-a1 == b1` bitwise: `u1_i XOR a1_i XOR s_i == b1_i`, with `s_(i+1)=MAJ(NOT(u1_i),a1_i,s_i)`, s0=False. This is the exact t0/dual-inverse circuit but expressed in Z3 Bool/BitVec, not CryptoMiniSat. Keep the existing QF_BV workflow, unseeded control, and solve budget; no new backend/workflow or source dispatch until the control passes.
