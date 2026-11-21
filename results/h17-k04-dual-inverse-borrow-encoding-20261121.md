# K04 xoroshiro128++ dual-inverse / direct-borrow encoding

**Status:** encoding-level result; SAT runtime and source recovery not yet established  
**Date:** 2026-11-21  
**Owner of coordinated solver experiment:** Agent 20

## Question

Can the existing first-pair xoroshiro128++ inversion be represented with materially fewer SAT variables and clauses, without changing the proposed generator, source rows, holdout policy, backend family, or acceptance commitment?

The source-specific hypothesis remains the same: the three PS-261003-0417 RECOVER rows at 18:01Z REQUESTED, 18:02Z ACK, and 18:03Z REQUESTED are consecutive 16-byte packets from one xoroshiro128++ output stream. The solve may use only the first packet's two 64-bit outputs. The predicted middle outputs (2,3) must be unique; the third packet's outputs (4,5) remain a blind holdout. This report changes only the circuit encoding.

## Algebraic reduction

For xoroshiro128++ output from state words `a` and `b`,

\[
y = \operatorname{ROTL}_{64}(a+b,17)+a \pmod{2^{64}}.
\]

Subtract `a`, rotate right by 17, and subtract `a` again:

\[
b = \operatorname{ROTR}_{64}(y-a,17)-a \pmod{2^{64}}.
\]

This is an exact identity, not a heuristic. Therefore one symbolic 64-bit state word `a0` determines the transition word `t0 = a0 XOR b0` directly, without materializing `b0`. Let `u0 = ROTR64(y0 - a0, 17)`; then `b0 = u0 - a0`, so `t0 = a0 XOR b0 = u0 XOR borrow`, where `borrow` is the borrow chain for `u0-a0`. Bitwise, `t0[i] = u0[i] XOR r[i]` and `r[i+1] = MAJ(~u0[i], a0[i], r[i])`, with `r0=0`. **Prior-art qualification:** Agent7's existing one-variable script already used the first-output inversion; that step is not claimed as new here. The incremental reductions are deriving `t0` directly, applying the inverse identity to the second output, fusing its difference with equality to actual `b1`, and using direct borrow gates. Apply the xoroshiro transition:

\[
a_1=\operatorname{ROTL}_{64}(a_0,49)\oplus t_0\oplus(t_0\ll21),
\]
\[
b_1=\operatorname{ROTL}_{64}(t_0,28).
\]

The second observed output (y_1) imposes the same inverse identity on the next state:

\[
b_1=\operatorname{ROTR}_{64}(y_1-a_1,17)-a_1.
\]

Thus the first-pair inverse is a 64-bit search over `a0`; `t0` is derived directly, and the second output is expressed as equality to the required `b1`. `b0` can be reconstructed as `a0 XOR t0` after solving if needed. Outputs 0 and 1 are not fitted through two forward-output adders.

## Direct borrow-chain encoding

The existing CryptoMiniSat circuit implemented subtraction as complement-plus-add (`a + ~b + 1`), allocating complemented-word variables and an initial carry variable. A direct subtractor uses the borrow recurrence.

For `d = a - b mod 2^64`, with `r0 = 0`:

\[
d_i=a_i\oplus b_i\oplus r_i,
\]
\[
r_{i+1}=\operatorname{MAJ}(\neg a_i,b_i,r_i).
\]

At bit zero, `r1 = ~a0 AND b0`, so a three-clause AND gate suffices. Later borrow bits use a six-clause majority gate with the first input represented as a signed literal `-a_i`; no complemented-word variables are needed.

For constant-minus-variable `u = c - a`, the difference bit is `u_i = c_i XOR a_i XOR r_i`, and the borrow recurrence specializes to:

- if `c_i=0`, `r_(i+1)=a_i OR r_i`;
- if `c_i=1`, `r_(i+1)=a_i AND r_i`.

The initial borrow is zero. This removes the 64-variable constant word and simplifies the carry chain.

For the first output, after computing `u0 = ROTR64(y0-a0,17)`, the subtraction `b0=u0-a0` need not materialize `b0`. The transition uses only `t0=a0 XOR b0`; substituting the difference bit gives `t0[i]=u0[i] XOR r[i]`, with `r[i+1]=MAJ(~u0[i],a0[i],r[i])`. This eliminates the 64 `b0` variables and the 64 separate `a0 XOR b0` variables, replacing them with the 63 non-alias `t0` XOR outputs.

For the second observed output, the required difference word need not be allocated at all. Let `u = ROTR64(y1 - a1, 17)`. The equality to actual `b1` is directly:

\[
u_i\oplus a_{1,i}\oplus r_i\oplus b_{1,i}=0,
\]

with the same borrow-out recurrence `MAJ(~u_i, a1_i, r_i)`. This fuses the second subtraction's difference equation with equality to the actual next-state word, eliminating 64 temporary variables and 64 extra XOR clauses.

## Keep the initial solve separate from uniqueness

The first SAT solve needs only:
1. symbolic `a0`;
2. derived `t0` directly, without materializing `b0`;
3. one xoroshiro transition to (`(a1,b1)`);
4. the second-output inverse equality.

It does **not** need state2/state3 or outputs2/3. After a first-pair model is found, compute outputs2/3 and outputs4/5 by forward replay. Check outputs4/5 against the untouched third REQUESTED packet as a blind holdout.

Only after the holdout check should a separate circuit build outputs2/3 and test middle uniqueness by adding one blocking clause over the complete 128-bit middle:
`Or(out2 != recovered2, out3 != recovered3)`.
Require UNSAT to establish uniqueness; SAT means a distinct middle; UNKNOWN remains unresolved. Do not substitute state uniqueness for middle uniqueness.

## Circuit-size comparison

The existing Agent50 CryptoMiniSat first-pair circuit from run 44931493564 contained 1,658 variables, 3,136 CNF clauses, and 1,024 XOR clauses. It built the middle-output circuit before the initial solve. That run's planted positive control returned UNKNOWN after 180.382 seconds.

The local reference encoding produced the following counts for the current synthetic planted control (both observed output words have least-significant bit 0):

| Circuit | Variables | CNF clauses | XOR clauses |
|---|---:|---:|---:|
| Existing first-pair circuit | 1,658 | 3,136 | 1,024 |
| Dual-inverse/direct-borrow/t0 first-pair core | **567** | **1,122** | **317** |
| Full circuit for middle uniqueness | 1,331 | 2,622 | 829 |

For the actual PS-0417 attempt-1 payload, [Agent35's independent source-view audit](../agents/agent35/k04_dual_inverse_count_audit.py) establishes the pre-`t0`-fusion counts and decoded constants. Applying the additional exact `t0` cancellation above removes 65 variables and 65 XOR clauses from each view; the resulting final counts are:

| Byte view | First zero bit in y0 / y1 | Core vars/CNF/XOR | Full vars/CNF/XOR |
|---:|---:|---:|---:|
| 0 | 1 / 0 | 566 / 1,119 / 317 | 1,330 / 2,619 / 829 |
| 1 | 1 / 0 | 566 / 1,119 / 317 | 1,330 / 2,619 / 829 |
| 2 | 0 / 1 | 566 / 1,119 / 317 | 1,330 / 2,619 / 829 |
| 3 | 0 / 1 | 566 / 1,119 / 317 | 1,330 / 2,619 / 829 |

All four current source views have the same final aggregate count. Their decoded attempt-1 words are view 0: `CD3E4F216ADB2FB1 / 80DA2AA90B33F7A4`; view 1: `B12FDB6A214F3ECD / A4F7330BA92ADA80`; view 2: `80DA2AA90B33F7A4 / CD3E4F216ADB2FB1`; view 3: `A4F7330BA92ADA80 / B12FDB6A214F3ECD`. The original byte view remains unresolved. Agent35 independently checked the pre-`t0` arithmetic and gate-count formulas; the additional `t0` cancellation is validated by the Agent36 reference script and is pending Agent35's review. These remain count audits, not SAT results.

Two successive fusions after the dual-inverse/direct-borrow baseline reduce the circuit. First, fusing the second-output difference with equality removes 64 materialized `required_b1` variables and 64 equality XOR clauses without changing CNF count: synthetic core 696 / 1,122 / 446 → 632 / 1,122 / 382; source core 695 / 1,119 / 446 → 631 / 1,119 / 382. Second, deriving `t0` directly removes 65 more variables and 65 XOR clauses, again with CNF unchanged: synthetic core 632 / 1,122 / 382 → 567 / 1,122 / 317; source core 631 / 1,119 / 382 → 566 / 1,119 / 317. The full source uniqueness circuit falls from 1,459 / 2,619 / 958 to 1,395 / 2,619 / 894 after the first fusion, then to 1,330 / 2,619 / 829 after the `t0` simplification. Agent35's independent adversarial review found no sign, carry, or rotation error in the fused equations; the final `t0` refinement has been sent for review.

The final source initial-inversion core is approximately 66% smaller in variables, 64% smaller in CNF clauses, and 69% smaller in XOR clauses than the existing full circuit. The full middle-uniqueness circuit is also smaller. These are exact gate counts from the local reference construction, not a prediction of proportional runtime improvement.

## Validation performed

- Agent35's independent source-view audit script uses deterministic seed `0x35D0A11` for 100,000 arithmetic checks; the direct subtraction and constant-minus-variable borrow recurrences matched 64-bit modular subtraction.
- Signed-literal majority, AND/OR, and constant-borrow gates passed exhaustive truth-table checks.
- The complete dual-inverse/fused-equality/t0-only reference circuit passed all emitted CNF and XOR witness checks on 100 deterministic 64-bit xoroshiro states generated with `random.Random(0xA17E2026)` by the [Agent36 reference script](../agents/agent36/k04_dual_inverse_borrow_reference.py).
- The reference circuit was checked against the same xoroshiro128++ (49,21,28) transition and output functions used by the existing solver.

No CryptoMiniSat or Z3 solve was run on this optimized encoding. The local runtime did not have pycryptosat or z3 installed, and package installation failed because DNS was unavailable. No planted-control SAT result, source result, K04 component, candidate edit, or verifier change is claimed.

## Limits and next step

This is an encoding-level result only. It does not establish that the PS-0417 payloads were emitted by xoroshiro128++, that the first pair has a unique middle, or that the source model predicts the third packet. It does not alter the PS-0417 row selection, the byte-view hypotheses, the recorded mask, or the K04 commitment.

Agent 20 owns the single coordinated solver experiment. The preferred no-new-workflow route is the existing gated first-pair Z3 workflow, with the dual-inverse identity integrated if selected. The direct-borrow circuit is a CryptoMiniSat-specific alternative and should not be run in parallel as another backend variant. The positive-control gate must pass before source execution. Keep solver status, middle uniqueness, blind-holdout status, ACK2-payload comparison, and component commitment status as separate fields. A genuine commitment hit must not be discarded solely because the source model fails its holdout; a hit with a failed holdout must not be called a validated first-pair reconstruction.

If the chosen optimized encoding still returns UNKNOWN on the same unseeded planted control, do not increase timeouts or proliferate backends. Close this solver line and reallocate to a different source-dependent constructor.

## References

- Reproducible standard-library-only circuit witness test: [Agent36 reference script](../agents/agent36/k04_dual_inverse_borrow_reference.py). It checks 100 deterministic planted states and exact circuit counts; it does not invoke a SAT solver.
- Existing CryptoMiniSat circuit: [Agent50 first-pair script](../agents/agent50/k04_xoroshiropp_first_pair_sft.py), [XOR-CNF circuit](../agents/agent50/k04_xoroshiropp_xorcnf_sft.py).
- Existing gated Z3 path: [Agent1 first-pair script](../agents/agent1/k04_xoroshiro128pp_z3_sft.py), [Agent20 manual workflow](../.github/workflows/agent20-k04-xoroshiropp-first-pair-manual.yml).
- Implementation discussions: [dual-inverse circuit](../communications/agent20/20261121T185531Z_agent36-dual-inverse-output-circuit.md), [fused equality](../communications/agent20/20261121T190122Z_agent36-fused-second-output-equality.md), [code sketch](../communications/agent20/20261121T185619Z_agent36-dual-inverse-code-sketch.md).
