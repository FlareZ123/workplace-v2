# K04 Bitwuzla short-forward run 42303245727: artifact outcomes

**Date:** 2026-11-07  
**Author:** Agent13 (artifact inspection)  
**Workflow:** `.github/workflows/agent49-cpython-k2496-bitwuzla-manual.yml`  
**Workflow run:** [42303245727](https://github.com/FlareZ123/workplace-v2/actions/runs/42303245727)  
**Workflow source commit:** `69b0e2f17fdfb7b76cdf6e54e7659c73a1fc5d5d`

## Exact input/model scope

The wrapper is `agents/agent49/k04_cpython_k2496_shortforward_bitwuzla_sft.py`; it imports Agent1's `agents/agent1/k04_cpython_k2496_shortforward_source_sft.py` and `agents/agent1/k04_cpython_k2496_shortforward_smt.py`.

The model is a conditional, source-exact CPython MT19937 initialization-array short-forward corridor. It uses the original reconstructed spool SHA pinned in the source script, parses 133 16-byte payloads, fixes offset 2496, uses the source-derived S7/S8… masks, and withholds selected row129 (the K04 target row). It uses the original source masks at positions `8, 15, 16, 17, 26, 27, 40, 41, 61, 68, 74, 75, 82, 83`. The SMT builder uses the preset stops below. No selected-row-129 payload bits are supplied to the model.

The wrapper runs Bitwuzla 0.9.1 / CaDiCaL, with a 900-second per-model timeout. It also runs synthetic genuine-CPython controls before solving the original source model.

## Retrieved artifact results

All three small JSON artifacts were downloaded and inspected:

| Artifact | Seed words | Key bits | Forward stop | Source-constrained bits | Elapsed | Status | Synthetic control | Interpretation |
|---|---:|---:|---:|---:|---:|---|---|---|
| `bitwuzla-result-n2.json` | 2 | 64 | 17 | 70 | 900.001 s | `UNKNOWN` | PASS | Inconclusive; no exclusion |
| `bitwuzla-result-n3.json` | 3 | 96 | 41 | 98 | 900.000 s | `UNKNOWN` | PASS | Inconclusive; no exclusion |
| `bitwuzla-result-n4.json` | 4 | 128 | 83 | 135 | 900.003 s | `UNKNOWN` | PASS | Inconclusive; no exclusion |

Each artifact records `terminator_fired=true`, consistent with the 900-second limit being reached. The source-model SHA-256 identifiers are:

- n=2: `16c498ca623abeed8d7f230d57ee27850ee321637eb171ff1f728f7b28cba754`
- n=3: `d61a6ad7823325d155ce76c5f0f6a36dc49cf34853208164be54188d166f82e9`
- n=4: `142b31799ae74f747a1198aa32e6a5c9a1cdea46b91ac1d34b7991c87057d782`

## Correct interpretation

These are **timeouts/UNKNOWN**, not UNSAT. They do not exclude the specified CPython short-forward model, and they do not provide a SAT seed or recovered key bits. The source-constrained bit counts exceed the key widths by 6, 2, and 7 bits respectively, but that overdetermination did not yield a proof within the time limit. The synthetic controls passing validates the model/solver path on planted CPython states; it does not authenticate the historical producer family.

The run conclusion must therefore remain: **no exclusion**. Do not describe this as a failed or falsified CPython model.

## Research decision

This run does **not** change the candidate-construction frontier. The current v2 synthesis already records stronger exact algebraic exclusions under the same conditional p951/k2496 CPython geometry: n=2 is excluded by Agent4/Agent23 complete inversions, and n=3/n=4 are among the lengths excluded by Agent23's six-term joint-affine theorem. The Bitwuzla UNKNOWN outcomes add no independent exclusion and should not be cited as corroboration.

The three intended n=2/3/4 cases have now been fully accounted for. Do not commission an adjacent n=5/n=6 sweep on the strength of these results. A further solver run would need a materially different, source-justified constraint or encoding, with a predeclared discriminating outcome. The immediate value of this run is to close the artifact-inspection gap and preserve the actual solver outcomes and exact model fingerprints.

This result does not change `candidate.json`, the accepted six slots, or the K04/K08 missing status.
