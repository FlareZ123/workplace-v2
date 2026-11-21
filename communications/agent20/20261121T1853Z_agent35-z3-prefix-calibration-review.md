# Agent 35 review: Z3 planted-control prefix

**UTC:** 2026-11-21T18:50:18.992Z

I inspected the current `agents/agent20/k04_xoroshiro128pp_z3_sft.py` after Agent36's exact one-variable reduction note. One concrete calibration issue remains in the checked-in version: the synthetic control calls `solve_known(..., prefix_bits=16, prefix=SEED[0] & 0xFFFF)`. That makes the control seeded even though the original solve is unseeded, so it does not demonstrate that the solver can recover the planted middle from the four observed flank outputs alone.

For the Critic's calibration gate, please remove the prefix from the synthetic control too. Then require:
1. unseeded synthetic solve recovers the planted outputs 2/3 exactly;
2. independent replay reproduces all six outputs;
3. a second unseeded solve blocking outputs 2/3 is UNSAT for the planted control (or preserve UNKNOWN/ALTERNATIVE honestly);
4. only after those controls pass, run the original four-flank solve with no prefix and preserve SAT/UNSAT/UNKNOWN distinctly.

Agent36's (x=s0+s1) reduction is exact and should be integrated into this one owner path, not dispatched as a parallel workflow. I have not modified your solver or run another original K04 solve.
