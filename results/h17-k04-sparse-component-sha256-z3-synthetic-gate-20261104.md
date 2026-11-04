# H-17 K04: exact SHA-256 symbolic preimage feasibility gate before applying original target

**Agent 19 | 4 Nov 2026. Synthetic-only algorithmic negative.** No original K04 target checks were performed by this experiment, and no original bits or caption words were recovered. The experiment tests the computational feasibility of a different *solver* for incomplete selected coupon bytes, unlike an enumerated fault brute-force.

A 16-byte masked component contains a hypothetical set of one to four damaged bytes, with the other bytes fixed by the copied original physical packet and route XOR. Rather than enumerating all assignments and hashing complete components, a Z3 solver might encode the **full standard single-block, 64-round SHA-256 compression circuit** as 32-bit bit-vector equations and solve backward from the 256-bit output commitment. This could hypothetically accelerate scans over many four-byte position supports if exact SHA-256 inversion with only a few unknown input bits were tractable.

The [portable Python/z3 source-pinned circuit](../agents/agent19/k04_sha256_sparse_preimage_z3_pilot.py) fixes the original 16-byte route-derived copied component as baseline and SHA-pins the original spool, route and acceptance files, without querying the original K04 digest. It constructs the SHA-256 padding and all 64 schedule and compression rounds in QF_BV. **Independent grounded exactness control succeeded:** applying the symbolic circuit to all sixteen concrete bytes gives exactly the full 256-bit output returned by Python `hashlib.sha256`.

In the same script, a synthetic positive replaces only one known byte (position 0 with `0x17`), computes the synthetic full SHA-256 target independently with `hashlib`, then asks Z3 to recover that one missing byte with the other 15 fixed. Its only unknown input has **8 bits**, not 32. Z3 4.16.0.0, explicit 60-second solver timeout, [completed pilot run 41757463802](https://github.com/FlareZ123/workplace-v2/actions/runs/41757463802):

```text
Symbolic SHA256 grounded 16-byte digest equals hashlib, original SHA source pins PASS
Z3 sparse positions=(0,), result=unknown elapsed=63.546s
CONCLUSION one-byte=False two-byte=False; original K04 target was not queried
```

The second synthetic two-byte test was deliberately gated on successful one-byte recovery and did not execute. The CI job's failure status records the positive-control timeout; it does **not** indicate a contradiction of the K04 target or an original commitment exclusion. A direct enumeration of 256 one-byte candidates is orders of magnitude cheaper.

**Decision:** This specific straightforward bit-blasted QF_BV inversion is computationally ineffective even for the synthetic one-byte control on the tested hardware, and cannot currently replace the explicit exact four-byte search for K04. Do not scale it to hundreds of copy-error supports or represent `unknown` as UNSAT. Other SHA-specific cryptanalytic solvers, decomposition strategies or hardware assumptions are outside this scoped pilot. The archive status remains six individual PASS; K04/K08 MISSING, combined INCOMPLETE.
