# K04 compact symbolic triad inversion: calibration result

Date: 2026-11-22  
Owner: Agent 17  
Workflow run: 45006451504  
Artifact: k04-compact-symbolic-triad (artifact ID 14747644321; ZIP SHA-256 043c01a7e97ac0e840770806c1ab0e55e01cf795887fca5fe310d80095fcf7cc)

## Question

Can a materially reduced native-XOR encoding make the existing conditional xoroshiro128++ reverse-triad model live on source-independent planted states, sufficiently to justify testing the historical PS-0417 source?

This was a solver-representation experiment only. It did not establish that the printer historically used xoroshiro128++, authenticate the selected ACK tail, or introduce a new source relation.

## Representation

The implementation in agents/agent17/k04_xoropp_linear_elimination_sft.py symbolically propagates the state trajectory as GF(2) expressions. It removes explicit variables for most intermediate XOR state-transition gates and materializes only the initial first state word, the necessary a/u carry-input words, and subtraction borrow chains.

The generated circuit had 755–759 variables, 1,671–1,683 CNF clauses, and 448 native-XOR clauses. The representative count was 758 / 1,680 / 448, versus the earlier reverse-triad representation's 943 / 1,671 / 636.

Both the local and workflow-side planted-witness checks passed 100 seeded circuit validations.

## Frozen calibration

The exact same eight frozen 128-bit states used by Agent 30 were tested without supplying the planted state to the solver. Each instance had a 120-second limit. A recovery counted only when the solver returned the exact initial state and replayed all six outputs exactly.

| Index | Status | Seconds | Exact state and six-output replay |
|---:|---|---:|---|
| 0 | UNKNOWN | 120.205 | — |
| 1 | UNKNOWN | 120.076 | — |
| 2 | UNKNOWN | 120.094 | — |
| 3 | UNKNOWN | 120.103 | — |
| 4 | SAT | 17.385 | PASS |
| 5 | UNKNOWN | 120.148 | — |
| 6 | UNKNOWN | 120.066 | — |
| 7 | UNKNOWN | 120.103 | — |

**Result: 1/8 exact recoveries; 7 UNKNOWN; 0 UNSAT.**

This is no liveness improvement over Agent 30's earlier 1/8 result. The smaller circuit and successful witness checks do not translate into a more reliable inversion.

## Historical-source gate

The historical PS-0417 source was **not evaluated**. The workflow required at least 6/8 exact planted recoveries before trying either endian view. That threshold was not met.

Consequently:
- no PS-0417 SAT result was obtained;
- no complete coupon was reconstructed;
- the original K04 SHA-256 commitment was not evaluated;
- the REQUESTED1 holdout was not evaluated;
- no K04 value is proposed.

K04 remains MISSING. This result neither confirms nor falsifies the historical xoroshiro hypothesis; it shows that this encoding does not provide a sufficiently live solver under the tested budget.

## Disposition

Retain the script as a reproducible reference for the symbolic-elimination encoding, but retire this solver lane. Do not create another workflow or tune variable order, random seeds, or time limits against the same eight-state/source assumptions. Reopen only if a new source-authenticated constraint, independently preserved PS-0417 media, or a materially different producer relation becomes available.

The one-off manual workflow is retired after this run. Canonical candidate data, acceptance commitments, verifier, and original evidence remain unchanged.
