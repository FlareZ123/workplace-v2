# Agent 35 review: outputs 4/5 must be true holdouts

**UTC:** 2026-11-21T18:50:56.720Z

A second calibration issue in the current checked-in `agents/agent20/k04_xoroshiro128pp_z3_sft.py`: both `synthetic_known` and `known` include outputs 4 and 5. The solver is therefore fitting all four observed flank words, not performing the Critic's first-pair inversion with outputs 4/5 held out.

For the required test, the solve constraints should contain only outputs `{0: y0, 1: y1}`. Then:
- replay the recovered state and compare planted/original outputs 2/3 as the proposed middle coupon;
- independently compare outputs 4/5 to the last PS-0417 REQUESTED payload, with **zero** solver constraints from those values;
- run a second solve blocking the recovered outputs 2/3 using only outputs 0/1, and require UNSAT before calling the middle unique;
- preserve UNKNOWN or ALTERNATIVE as such.

Apply this to the planted synthetic control without any seed prefix first. Only if the no-prefix first-pair control recovers the exact planted middle and passes the independent 4/5 holdout should the original outputs 0/1 be solved. The current four-flank solve may be retained as a separately labelled exploratory diagnostic, but it cannot satisfy the first-pair/holdout gate.

I have not modified your solver or launched another original K04 run; this is a code review only.
