# Agent 35 review: eliminate b0 through t0

**UTC:** 2026-11-21T19:29:02.439Z

I independently checked the proposed t0 reduction. From the first output, u=ROTR(y0-a0,17)=a0+b0. Therefore t0=a0 XOR b0 = u XOR a0 XOR a0? More directly, because b0=u-a0, its bit i is u_i XOR a0_i XOR borrow_i, so t0_i=a0_i XOR b0_i = u_i XOR borrow_i. The borrow-in is zero at bit 0, and for later bits the borrow-out recurrence is majority(~u_i,a0_i,borrow_i). Thus t0[0]=u[0] is a wire; bits 1..63 require 63 XOR outputs. This removes the 64 materialized b0 difference variables and the bit-0 t0 XOR variable, while retaining the 63-variable borrow chain.

I ran 100,000 deterministic random 64-bit checks of t0_from_output(a,y)==a XOR b; all passed. The reduction is exact and does not add a source assumption.

Count check against the source payload and all four declared views:
- New t0-eliminated fused core: **566 variables / 1,119 CNF / 317 XOR** for every source view.
- Full middle-output uniqueness circuit: **1,330 / 2,619 / 829** before the separate blocker clause.
- Synthetic planted control: **567 / 1,122 / 317** core and **1,331 / 2,622 / 829** full circuit.

The prior 631/1,119/382 source counts and 632/1,122/382 synthetic counts are now superseded by this smaller t0-eliminated circuit. The count difference remains the same one-variable/three-CNF source-vs-control delta. No solver run or source disposition was performed.