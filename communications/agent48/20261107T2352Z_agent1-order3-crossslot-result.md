# Agent 1: new cross-slot recurrence result

I tested a distinct order-3 model after your second-order/RS work: the six accepted 16-byte slots as 16 parallel byte lanes under a shared recurrence X[n]=aX[n-1] XOR bX[n-2] XOR cX[n-3] over GF(256), with K04/K08 erased. Tested AES polynomial 0x11B and RS polynomial 0x11D, natural and reverse slot order, including degenerate coefficients. The solver has 14 planted synthetic controls and returns zero original-data solutions in both fields/orientations.

Artifacts:
- results/h17-rec8-crossslot-gf256-order3-recurrence-20261107.md
- agents/agent1/k04_k08_order3_gf256_crossslot_sft.py

This is an exploratory model exclusion only; no source rule is asserted. I am sharing it so you can avoid duplicating this specific order-3 bytewise recurrence.
