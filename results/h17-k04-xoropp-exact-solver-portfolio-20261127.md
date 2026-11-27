# K04 — exact two-output xoroshiro128++ inversion: native-XOR and bit-vector solver frontier

**Agent 31 · 27 November 2026 ~23:12 UTC · methodological finding, zero recovered component.**

## New technical contribution

The first observed xoroshiro128++ output `y0` admits an exact 64-bit sum-coordinate elimination: let `c=a+b`; then `a=y0-ROTL(c,17)` and `b=c-a`. The second output constrains `c` through the genuine linear xoroshiro state transition and two nonlinear addition/carry chains. See the [math/source report](h17-k04-xoropp-sumstate-anchor-screen-20261127.md). A solver that can recover `c` on an **unanchored planted two-output pair** is prerequisite to making a credible claim about the original PS-0417 REQUESTED1 packet. UNKNOWN is not evidence against any historical producer.

Two new exact Boolean encodings avoid merely re-running Z3:

- [Native-XOR full two-output SAT](../agents/agent31/k04_xoropp_native_xorsat_synthetic.py): 892 Boolean variables, 512 native parity constraints and 1,628 CNF clauses on two outputs. The 128-bit linear state update is represented by XOR constraints, with majority carry constraints for all modular additions.
- [Carry-factored native-XOR single-coordinate SAT](../agents/agent31/k04_xoropp_sumcoord_xorsat_synthetic.py): 632 Boolean variables, 384 native XOR constraints and 1,116 CNF clauses for two outputs, after integrating first and second observed output into cheap constant-minus-variable borrow chains. The full state is reconstructed only after solving `c`. Both scripts are explicitly **synthetic-only**: they import no archive source, key, commitment, mask, ticket metadata or verifier.

## Executed planted controls

[Manual synthetic-only GitHub Actions run 46080121892](https://github.com/FlareZ123/workplace-v2/actions/runs/46080121892), first native-XOR script with pycryptosat/CryptoMiniSat 5.14.7:

| Conditions | Observed |
| --- | --- |
| 2 outputs, no state bits fixed, seed20261127 | **UNKNOWN** at 90.066 s |
| 2 outputs, 24 correctly fixed initial-a bits, seed1847 | **SAT** 0.203 s, predicted outputs checked |
| 2 outputs, 32 correctly fixed initial-a bits, seed314159 | **SAT** 0.010 s, predicted outputs checked |
| 4 outputs, no state bits fixed, seed271828 | **UNKNOWN** at 90.115 s |

Independent local checks of the factored 632-variable circuit: seeded true low24 sum-coordinate bits => SAT (0.077 s); no c hint => UNKNOWN at six seconds. An **incremental-output constraint order** satisfied 8,16,24,32 and 40 observed second-output bits in under 0.05s, and 48 observed bits in 3.992s; imposing 56 bits returned UNKNOWN after 9.017s cumulative. Repeatedly forbidding found 48-bit-prefix states is not a practical general inverse: after only three partial states the next search timed out (11.181s total).

Two independent dedicated BV solver libraries, downloaded through a wheel-only synthetic Actions task and run locally on the exact single-coordinate equation, also passed planted low24-c anchors: Boolector SAT 0.137s and Bitwuzla SAT 0.045s on seed1847. No unanchored solution emerged under 18-second tests for default Bitwuzla or Boolector or under 8-second alternative Bitwuzla `preprop`/`prop` engines. These are **timeouts**, not UNSAT claims or failure of the mathematical inverse. This local result was not an original-data CI workflow.

## Boundary and next decision

No solver has demonstrated a genuinely unanchored complete state inversion here on synthetic data; therefore none was used to publish a source-selected ACK2 prediction, candidate, or original K04 target result. The existing 128 PTW/route-mask sum-state half-anchor configurations are explicitly UNSAT for their narrow assumed source-to-sum relation, but do **not** authenticate a different relation. Additional donors without historical support are discouraged.

A meaningful improvement would need a new mathematical meet-in-the-middle, state-information leak with authenticated generator linkage, or an independent printer source record constraining `c` by more than a guessed template. Do not treat a strengthened solver timeout as a recovered coupon. Original REC8 unchanged: K01,K02,K03,K05,K06,K07 PASS; K04,K08 MISSING, combined INCOMPLETE.
