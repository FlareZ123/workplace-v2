# H-17 K04: center-pivot bidirectional xoroshiro128++ triad, frozen liveness gate

**Agent 1 | 22 November 2026 | complete execution, original K04 NOT_EVALUATED**

## Concrete inversion change

The retained printer spool contains the attempt-2 ACK selected for K04, with disputed copied integrity. This experiment instead supposes that the third word of the selected attempt-2 coupon and both subsequent REQUESTED3 words are consecutive outputs of the **same xoroshiro128++ 1.0 producer**, at output positions 3, 4 and 5. This is a conditional machine model; no native printer source attests the producer or the copied ACK tail.

Unlike earlier left-anchored triad circuits, the inverse anchors its **middle observed output 4** and fits one earlier and one later output. For a 64-bit xoroshiro state \`(a,b)\`, define \`t = a XOR b\` and \`y = ROTL64(a+b,17)+a mod 2^64\`. For known middle output \`y4\`, the unknown 64-bit \`a4\` gives \`u4 = ROTR64(y4-a4,17)\`, \`t4=u4-a4\`, and \`b4=a4 XOR t4\`. The exact linear state transition is \`a5 = ROTL64(a4,49) XOR t4 XOR (t4<<21)\`, \`b5=ROTL64(t4,28)\`. Inverting it gives \`t3=ROTR64(b4,28)\`, \`a3=ROTR64(a4 XOR t3 XOR (t3<<21),49)\`, and \`b3=a3 XOR t3\`. The circuit asserts the exact output3 and output5 equations with native XOR clauses and CNF arithmetic borrow/carry constraints.

The solver reconstructs the complete 128-bit generator state at output4, steps backward to output0, and regenerates all six outputs. If a historical original source SAT were produced, the program would assemble **both selected coupon words**, XOR the **original unchanged K04 mask**, and hash the resulting complete 16-byte component against the unchanged official SHA-256 target **regardless of a speculative earlier REQUESTED1 holdout**. The holdout remains a separate annotation.

## Executed frozen controls

Reproducer: [\`agents/agent1/k04_center_pivot_triad_sft.py\`](../agents/agent1/k04_center_pivot_triad_sft.py).

Preserved original [one-shot Actions run 45006285559](https://github.com/FlareZ123/workplace-v2/actions/runs/45006285559), success as an execution, machine-result artifact ID **14748336391**. Workflow dispatched as manual-only and deleted after its single execution; program remains.

- Five seeded state/circuit forward and backward witness checks: **PASS**.
- Four distinct precommitted, unseeded, hidden-state planted output3/4/5 controls: **all four UNKNOWN at about 120 seconds each**.
- Circuit sizes per original frozen state: **947/944/946/946 variables**, **636 XOR clauses** each and **1,683/1,674/1,680/1,680 CNF clauses**.
- Complete exact hidden-state recoveries **0/4**, compared with prior left-anchored triad's **1/4** exact states on the same four controls and budget.
- The source gate required at least two unseeded controls and at least one previously unsolved control. It correctly skipped the actual printer source because the gate failed. Therefore **no original K04 coupon, no complete original component digest check, no blind REQUESTED1 holdout and no K04 failure against the original target** arose from this experiment.

These UNKNOWN results are solver-liveness failures, not logical UNSAT or evidence against the hypothesized historical generator.

## Decision

The center-pivot change is a measured **liveness regression** for this conditional producer at the same frozen budget. Do not rerun it at extended timeout, substitute another solver to report the same source guess, treat seeded witness validation as an unseeded recovery, or report the original K04 commitment as having been tested. Further effort should require a historically new target-bearing constraint or a different source producer and an actual full-component SHA-256 hit.

**Archive state unaffected:** K01/K02/K03/K05/K06/K07 independently PASS; K04 and K08 MISSING; combined REC8/1 INCOMPLETE. Official source, acceptance, route, verifier and candidate unchanged.
