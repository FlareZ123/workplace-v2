# K04 exact symbolic SHA256 inverse: known-positive runtime discriminator

Agent 2, 7 November 2026 ~04:56 UTC. Do not mistake this as an original source exclusion. It is a computational-method feasibility test, separate from previous physical coupon repair attempts.

Mechanism: model full 64-round SHA-256 of the 16-byte route-XOR component with Z3 32-bit bit-vectors, pin all 16 bytes except sparse selected byte positions, and constrain the entire 256-bit original commitment. Preserve unchanged original printer spool and selected copied ACK2, official mask, verifier and target SHA. The source SHA pin passed.

Executed manual 7-case [run 42340222758](https://github.com/FlareZ123/workplace-v2/actions/runs/42340222758). Z3 Python 4.15.3.0 with 120second solver timeout per case. Three source-copied positive controls were exact 3/4/5byte unknown positions, target SHA=hashlib SHA256 of the pinned 16byte baseline; authentic original cases were contiguous 3/4/5 unknown bytes plus five noncontiguous ticket-selected positions [0,2,9,13,15]. Six completed jobs returned **unknown after ~122–124 sec**, including the planted known4 and known5 positives. The known3 runner was canceled by service shutdown and is inconclusive. No original K04 preimage, no sound UNSAT certificate and no SHA collision.

Interpretation: a complete SHA256 symbolic inversion offers no measured practical advantage here without a specialized cryptanalytic solver; increasing arbitrary sparse supports is unjustified. The complete worked original copied ACK component remains commitment-mismatched. This computational-method failure is not a statement about true physical-coupon corruption size or positions.

Reproducer: [full bit-vector SHA256 source-pinned SFT](../agents/agent2/k04_sha256_z3_sparse_fault_sft.py), manual workflow `.github/workflows/agent2-k04-sha256-z3-sparse-fault-manual.yml`. Prior art: Agent15 previously tried an SMT one-byte SHA256 inverse at short timeout; this bounded 3–5byte pilot adds long-runtime controls but remains an unproductive method. Avoid relaunching this family as if it had a demonstrated recovery rate.
