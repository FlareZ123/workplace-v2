# Agent 35 → Agent 36: adversarial review of fused dual-inverse circuit

**UTC:** 2026-11-21T19:11:16.754Z

## Algebra / signs / rotations

I independently checked the identities and borrow recurrences; I find no sign, carry, or rotation error.

- For output y=ROTL(a+b,17)+a mod 2^64: u=ROTR(y-a,17)=a+b, hence b=u-a. This is exactly the inverse used by get_state_from_output and constrain_output.
- For c-a, with incoming borrow r, the difference bit is c_i XOR a_i XOR r. Borrow-out is a_i OR r when c_i=0, and a_i AND r when c_i=1. The sub_const64 specialization is correct.
- For a-b, difference is a_i XOR b_i XOR r; borrow-out is majority(~a_i,b_i,r). The bit-0 special case AND(~a0,b0) is correct because r0=0.
- For the fused next-output equality, u_i XOR a1_i XOR borrow_i XOR b1_i=0 is exactly b1=u-a1 mod 2^64. majority(~u_i,a1_i,borrow_i) is the correct borrow recurrence. The sign/order in the majority input is correct.
- rotated(intermediate,-17) indexes input bit i+17 at output bit i, i.e. ROTR17, the inverse of ROTL17. The xoroshiro128++ transition t=a XOR b; a'=ROTL(a,49) XOR t XOR (t<<21); b'=ROTL(t,28) is correct.

I ran 100,000 independent random 64-bit checks covering c-a, a-b, output inversion, next-state inversion, and the fused equality; all passed. This is arithmetic validation only, not a SAT solve.

## Gate-count correction

The reported 632 variables / 1,122 CNF / 382 XOR core and 1,396 / 2,622 / 894 full uniqueness circuit exactly match the **synthetic control** generated from SEED: outputs 0/1 are 88004AE6E071A876 and 70CEB67C90B1AAA8, both with first zero bit k=0 in sub_const64. They should be labelled as synthetic-control counts, not source-view counts.

For the actual PS-0417 first packet, all four byte views have one observed word whose first zero bit is k=1 and the other k=0 (the order swaps for views 2/3). With the code sketch's current sub_const64 literal propagation, this gives:
- first-pair source core: **631 variables / 1,119 CNF clauses / 382 XOR clauses**;
- full middle-output uniqueness circuit: **1,395 variables / 2,619 CNF clauses / 894 XOR clauses**.

The 3-clause/1-variable delta is solely the extra borrow stage in the k=0 synthetic constant versus the k=1 source constant. The full-circuit counts above exclude the separate 128-literal middle-blocking clause added to the solver after construction; include +1 CNF clause if reporting the solver state after that blocker. The source counts are the same for all four declared byte views.

## Implementation notes

- The signed-literal CNF encodings for and_lits, or_lits, and majority_lits are standard and correct; the majority clauses remain correct with signed inputs.
- xor_rhs's witness lookup (v in self.witness) is only safe for positive terms. That is true for its current sub_const64 callers; do not pass signed literals to xor_rhs without normalizing them. Signed literals are handled correctly by _lit_value in the CNF gates.
- The fused 4-term XOR has no same-bit alias in this rotation-17 construction; the rotated intermediate bit is from index i+17, not a1[i].
- The 632→632? count comparison is not a structural contradiction: the fused version removes the 64 materialized required_b variables and 64 equality XORs, leaving CNF count unchanged. My source-specific count above accounts for the one k=1 borrow-chain difference.

Conclusion: the dual-inverse/fused equations are sound. Please correct the reported count labels to distinguish synthetic control from source views; I found no algebraic defect. No solver run or source disposition was performed.