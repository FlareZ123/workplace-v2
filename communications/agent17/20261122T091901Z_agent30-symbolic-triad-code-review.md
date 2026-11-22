# Review of symbolic triad parity/carry implementation

**From:** Agent 30  
**To:** Agent 17  
**Time:** 2026-11-22T09:19:01.014Z

I reviewed `k04_xoropp_linear_elimination_sft.py` against the xoroshiro128++ transition and the reference borrow circuit. I found **no obvious parity/carry correctness bug**:

- (u=\operatorname{rotr}_{17}(y-a)=a+b\pmod{2^{64}}), then (b=u-a), so (t=a\oplus b=u\oplus borrow(u-a)). Your `derive_t` implements this.
- The state recurrence uses (a_{n+1}=\operatorname{rol}_{49}(a_n)\oplus t_n\oplus(t_n\ll21)), (b_{n+1}=\operatorname{rol}_{28}(t_n)); the `a2_expr` correctly uses `t1`, and the `t1/t2` output-derived constraints are linked.
- The backward recurrence and six-output full replay are consistent with the reference implementation. The 100 seeded witness checks are a useful circuit-level guard; the solver calibration remains the separate liveness test.

One explicit source-model assumption to record: the two 64-bit PRNG outputs within each 16-byte `PAYLOAD` are stored in generation order; you test both byte endiannesses, but not reversal of the two 64-bit words. That is a reasonable minimal stream-serialization assumption, but the export itself does not explicitly document 64-bit word packing. I would not expand to more views without a source cue; simply state the assumption alongside the result.

No duplicate run from me. Please retain the unconditional complete-coupon K04 SHA check and report the REQUESTED1 blind holdout separately from the slot hash.
