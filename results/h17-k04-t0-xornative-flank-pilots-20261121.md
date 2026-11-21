# H-17 K04: direct-borrow native-XOR inversion, unseeded planted calibration

**Agent50 | 21 November 2026, 23:47 UTC | K04 unchanged, no source candidates computed**

## New experiment and discriminating question

The earlier QF_BV-Z3 integration of Agent35/36's exact t0 borrow-chain reduction timed out on an unseeded planted xoroshiro128++ state after 300.004 seconds. Could a native XOR/Boolean SAT engine invert the same mathematically smaller circuit, or could explicitly fitting both intact REQUESTED packets around the disputed ACK improve inversion sufficiently to recover a complete middle coupon?

Use the exact source candidate model only as a hypothesis: outputs0/1 are the two 64-bit words of PS-261003-0417 18:01Z REQUESTED, outputs2/3 are the unknown 18:02Z ACK coupon, outputs4/5 are 18:03Z REQUESTED. Historical packet endian and word order are not established. The original 18:02 ACK2 copied buffer is **never used to fit the state**. The official XOR mask and unmodified K04 SHA256 commitment must be checked against each recovered complete middle candidate before comparing any copied ACK or deciding model uniqueness/holdout authenticity.

## Arithmetic and reproducible circuit

The first output obeys:

    u0 = ROTR64(y0 - a0, 17)
    t0 = a0 XOR (u0 - a0) = u0 XOR borrow(u0-a0)

with b0 = a0 XOR t0, next state (a1,b1) = (ROTL49(a0) XOR t0 XOR (t0<<21), ROTL28(t0)), and second observed output imposes:

    ROTR64(y1-a1,17) - a1 == b1

The direct-borrow gates are exact modulo-2^64 equations, checked against 100 independent seeded original-style states in [Agent36's witness circuit](../agents/agent36/k04_dual_inverse_borrow_reference.py) and 100,000 arithmetic controls in Agent35's independent review. This new [Agent50 native runner](../agents/agent50/k04_direct_borrow_xornative_sft.py) imports that reference circuit and uses **CryptoMiniSat 5.14.7 native XOR clauses** (pycryptosat) on a GitHub-hosted runner; it does not translate XORs into bit-vector equality or construct middle output logic inside the initial solver. A seeded circuit witness is checked before each real unseeded inversion.

Two separate conditions were predeclared, executed once each, and gated on successful recovery of the withheld seeded synthetic state:

| Calibration branch | Fitted output words | Boolean variables / CNF clauses / XOR clauses | Real solve duration | Planted status | Source jobs |
| --- | --- | --- | ---: | --- | --- |
| Native first-pair | 0,1 only | 567 / 1,122 / 317 | 180.151 s | **UNKNOWN / timeout** | **SKIPPED** |
| Native both-flank conditioned | 0,1 and 4,5 | 1,517 / 2,238 / 1,147 | 180.145 s | **UNKNOWN / timeout** | **SKIPPED** |

The second branch advances the symbolic state to outputs4 and5 and applies both additional fitting constraints. Outputs4/5 are conditioned source observations, without an independent holdout, in that branch. The first branch keeps outputs4/5 for a blind check only after a SAT state. Both branches use source-independent planted generator outputs and withhold the planted state from the solver. The four-flank model's additional 950 variables, 1,116 CNF and 830 XOR clauses did **not** provide SAT convergence in the same 180-second budget.

Executed artifacts:
- [GitHub Actions native first-pair run 44962908871](https://github.com/FlareZ123/workplace-v2/actions/runs/44962908871), commit 6668da7608ba966652ff3cd6e2e8027d85af9a21, control artifact 14730626555, concluded FAILURE because its required positive assertion correctly rejected UNKNOWN.
- [GitHub Actions conditioned both-flank run 44963154827](https://github.com/FlareZ123/workplace-v2/actions/runs/44963154827), commit 1c49755791e98682c7aecf9424887350110dda4d, control artifact 14730557317, same deliberate gate FAILURE on UNKNOWN.
- Both use the single [control-gated workflow](../.github/workflows/agent50-k04-t0-xor-native-control.yml), with parameter fit_flank=false or true; pinned dependency pycryptosat==5.14.7, Python3.12, single solver thread. The first run used an earlier script snapshot without the optional fitted-flank branch; the second used the additive source/workflow commits. No unexpected package, Python or clause errors occurred.

## Decision and scope

**No model was returned in either unseeded planted test, so no complete historical K04 coupon was generated, no original-source view was executed, no historical K04 component was hashed, and component_commitment_status=NOT_EVALUATED.** UNKNOWN is a computational limitation, not a source UNSAT, source commitment MISS, or evidence the historical printer did or did not use xoroshiro128++.

These runs close the fixed-budget native-XOR t0/first-pair and both-flank formulations as practical source producers. The Z3 direct-borrow 300-second run and earlier unoptimized XOR/meet efforts suffered the same planted-inversion limitation. Another routine timeout increase or equivalent backend would not advance recovery. Pursue a fundamentally different inversion method with demonstrable unseeded planted liveness or an independent complete-byte source/copy-stage reconstruction. The original source, six accepted components, candidate, acceptance and verifier remain unchanged.
