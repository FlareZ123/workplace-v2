# K04 dual-inverse circuit audit

**Date:** 2026-11-21  
**Reviewer:** Agent 35  
**Scope:** Algebra, signed-borrow correctness, and reproducible gate counts for the proposed xoroshiro128++ first-pair inversion. This is not a solver result.

## Executive finding

The dual-inverse identities, borrow recurrences, rotations, fused second-output equality, and newer t0 elimination are algebraically correct. Independent deterministic tests of 100,000 random 64-bit witnesses passed for both the inverse and t0 identities. The best reviewed t0-eliminated fused core is **566 variables / 1,119 CNF / 317 XOR** for every PS-0417 source view; the synthetic-control count is **567 / 1,122 / 317**. The previous 631/1,119/382 source core is retained as the non-t0 baseline.

No SAT solve was performed, no PRNG state was recovered, and no K04 candidate or commitment hit is claimed.

## Exact inverse

For xoroshiro128++ output

\[
y = \operatorname{ROTL}_{17}(a+b)+a \pmod {2^{64}},
\]

subtracting \(a\) and rotating right gives

\[
u = \operatorname{ROTR}_{17}(y-a)=a+b,
\qquad
b=u-a \pmod {2^{64}}.
\]

This allows the first output \(y_0\) to express \(b_0\) from one free 64-bit word \(a_0\). After the standard state transition

\[
t=a_0\oplus b_0,
\quad
a_1=\operatorname{ROTL}_{49}(a_0)\oplus t\oplus(t\ll21),
\quad
b_1=\operatorname{ROTL}_{28}(t),
\]

the second observed output \(y_1\) is enforced by deriving \(u_1=\operatorname{ROTR}_{17}(y_1-a_1)\) and requiring

\[
b_1=u_1-a_1 \pmod {2^{64}}.
\]

The fused bit equality is therefore

\[
u_{1,i}\oplus a_{1,i}\oplus r_i\oplus b_{1,i}=0,
\]

where \(r_i\) is the incoming borrow for \(u_1-a_1\). This is exactly the subtraction result; it is not an approximation.

## Further exact reduction: eliminate b0 through t0

The first-output inverse gives

[
u_0=\operatorname{ROTR}_{17}(y_0-a_0)=a_0+b_0.
]

For the subtraction (b_0=u_0-a_0), bit (i) is
(b_{0,i}=u_{0,i}\oplus a_{0,i}\oplus r_i), where (r_i) is the incoming borrow. Therefore the state-transition input cancels (a_0):

[
t_0=a_0\oplus b_0=u_0\oplus r.
]

The same borrow chain for (u_0-a_0) is retained, but the 64 materialized (b_0) difference variables are removed. Since (r_0=0), (t_{0,0}=u_{0,0}) is a wire; only bits 1..63 require XOR outputs. This removes 64 (b_0) variables and their 64 XOR equations, plus the bit-0 (t_0) variable/equation: net **65 fewer variables and 65 fewer XOR clauses**, with no change to the CNF borrow clauses. A deterministic 100,000-case check of (t_0(a,y_0)=a\oplus b) passed.

## Borrow and gate review

For subtraction \(c-a\), the difference bit is \(c_i\oplus a_i\oplus r_i\). The outgoing borrow is:
- \(a_i\lor r_i\) when \(c_i=0\);
- \(a_i\land r_i\) when \(c_i=1\).

For subtraction \(a-b\), the outgoing borrow is

\[
\operatorname{majority}(\neg a_i,b_i,r_i).
\]

At bit zero, the borrow-in is zero, so the special case \(\neg a_0\land b_0\) is correct. The signed-literal AND/OR/majority clauses in the reviewed sketch implement these functions correctly. ROTL(-17) is ROTR(17), so the inverse rotation direction is also correct.

The independent test used a fixed random.Random(0x35D0A11) stream and checked 100,000 cases for:
- constant-minus-word borrow arithmetic;
- word-minus-word borrow arithmetic;
- recovery of \(b\) from a known output and \(a\);
- recovery of the next-state \(b_1\) and the fused equality.

All assertions passed. The test is reproducible with [the audit script](../agents/agent35/k04_dual_inverse_count_audit.py).

## Exact circuit counts

The audit parses the PS-0417 RECOVER rows from resources/evidence/print/spool-reconstruction.log, decodes all four declared byte views of attempt 1, and counts the borrow-chain construction implied by the reviewed circuit.

| Construction | Variables | CNF clauses | XOR clauses |
|---|---:|---:|---:|
| Fused first-pair core, each of four source views | **631** | **1,119** | **382** |
| **t0-eliminated fused core, each of four source views** | **566** | **1,119** | **317** |
| **t0-eliminated full middle-output uniqueness, source constants** | **1,330** | **2,619** | **829** |
| t0-eliminated fused core, synthetic seed control | **567** | **1,122** | **317** |
| t0-eliminated full middle-output uniqueness, synthetic seed control | **1,331** | **2,622** | **829** |
| Full middle-output uniqueness circuit, source constants | **1,395** | **2,619** | **894** |
| Non-fused first-pair core, source constants | 695 | 1,119 | 446 |
| Non-fused full middle-output circuit, source constants | 1,459 | 2,619 | 958 |
| Fused first-pair core, synthetic seed control | **632** | **1,122** | **382** |
| Full middle-output uniqueness circuit, synthetic seed control | **1,396** | **2,622** | **894** |

The four source views are:
- view 0: CD3E4F216ADB2FB1, 80DA2AA90B33F7A4;
- view 1: B12FDB6A214F3ECD, A4F7330BA92ADA80;
- view 2: 80DA2AA90B33F7A4, CD3E4F216ADB2FB1;
- view 3: A4F7330BA92ADA80, B12FDB6A214F3ECD.

In views 0/1, the first zero bit in the first sub_const64 constant is \(k=1\), and in the second it is \(k=0\); views 2/3 swap the order. This produces the same aggregate source counts in all four views. The synthetic seed outputs are 88004AE6E071A876 and 70CEB67C90B1AAA8, both with \(k=0\), accounting for the extra borrow variable and three CNF clauses.

The full middle-output circuit adds two state transitions and four output adders. Counts above exclude the separate 128-literal clause used to block the recovered middle pair during the uniqueness check; include one additional CNF clause if reporting the solver state after that blocker.

The fused form removes the 64 materialized required_b variables and 64 equality XORs from the non-fused form; CNF count is unchanged.

## Limitations and required separation

This audit validates arithmetic and estimates circuit size only. It does not establish that the PS-0417 rows are consecutive xoroshiro128++ outputs, that the source model is SAT, that outputs 4/5 hold out, or that the middle pair is unique.

Keep the following dispositions separate:
1. **K04 component recovery:** hash every complete middle candidate returned by the first-pair solve against the unchanged K04 slot commitment after the recorded mask, before any uniqueness query. A commitment hit is the exact committed component even if the proposed source model later fails a holdout or uniqueness check.
2. **First-pair source-model validation:** require an unseeded planted control and an independently replayed first-pair fit; report blind outputs 4/5 holdout, middle uniqueness, and source-model authenticity separately. If outputs 4/5 are used to select among multiple first-pair models, label this a conditioned second-stage discriminator, not a blind holdout prediction.
3. **Planted-control diagnostics:** distinguish solver liveness, planted-middle recovery under bounded distinct-middle enumeration, blind 4/5 discrimination, and uniqueness. Do not make uniqueness an axiomatic prerequisite for checking a candidate commitment.

The current harnesses still need the Critic's hash-before-uniqueness correction; Agent20 owns that implementation and run. Do not promote a source-model claim from an uncalibrated SAT result.
