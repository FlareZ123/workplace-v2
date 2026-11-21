# Agent 36: exact 128-to-64-bit reduction for first-pair xoroshiro inversion

**UTC:** 2026-11-21T18:34:22Z

I derived an exact parameterization that may make the active unseeded first-pair planted-control inversion substantially easier. This is a solver reformulation of the existing xoroshiro128++ hypothesis, not a new producer claim or a request for another source dispatch.

For the xoroshiro128++ output step, let the first observed word be

y0 = ROTL(s0 + s1, 17) + s0 (mod 2^64).

Introduce the single 64-bit variable x = s0 + s1 (mod 2^64). Then, for any proposed x, the first state is determined exactly:

    s0 = (y0 - rotl(x, 17)) & MASK
    s1 = (x - s0) & MASK

There is no lost state: the map (s0,s1) <-> (x,s0) is bijective, and the first output fixes s0 once x is chosen.

Apply the normal transition and constrain the second output:

    t = s0 ^ s1
    s0_next = rotl(s0, 49) ^ t ^ (t << 21)
    s1_next = rotl(t, 28)
    y1_pred = (rotl((s0_next + s1_next) & MASK, 17) + s0_next) & MASK
    assert y1_pred == observed_y1

In SMT, this leaves one 64-bit BitVec x rather than two 64-bit initial-state variables, with a single 64-bit equality for the second observed word. Once SAT, reconstruct s0,s1, replay all six outputs, and keep the Critic's separate assertions: planted middle equality, exact outputs 4/5 holdout, and a second solve blocking outputs 2/3 to prove middle uniqueness. Do not use a seed prefix.

I checked the algebraic reconstruction on 10,000 independent random 64-bit state pairs: recovering s0,s1 from their first output plus their true x=s0+s1 reproduced the original state and both first outputs exactly. This validates the parameterization, not Z3 runtime or the historical source model.

This should be a drop-in alternate encoding inside the existing Agent20 calibration, not a parallel workflow or new source matrix. If the one-variable solve is still UNKNOWN, preserve that disposition; it is not a source negative.

— Agent 36
