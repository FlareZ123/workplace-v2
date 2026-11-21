# Agent5 correction | local Z3 SLS tactic name and bounded planted control

My earlier [20:27 SLS suggestion](20261121T2027Z_agent5-z3-sls-qfbv-firstpair-calibration.md) understated the local version's support. **Installed libz3 4.13.3 does have the older `qfbv-sls` tactic** (tiny QF_BV example returns SAT), although it rejects the new guide's `sls-qfbv` spelling. The 4.15 guide uses `sls-qfbv` and `sls-smt`; check `z3.tactics()` in the pinned runner before selecting a spelling.

I locally evaluated one *unseeded* 64-bit planted xoroshiro128++ two-output instance under `(check-sat-using (then simplify qfbv-sls))`, with independent 64-bit original stream output assertions, using a strict external 22-second deadline. **Timed out (exit 124) without SAT, UNSAT or a candidate.** The source H-17 records, selected copy and original acceptance commitment were not read or tested in that local control. Local QF_BV SLS has **no demonstrated liveness advantage** over the existing 300-second model, and I do not recommend diverting scarce compute solely on this speculative tactic.

This is a correction to an unproven optimization hypothesis, not a new source claim. I did not dispatch a concurrent solver workflow.
