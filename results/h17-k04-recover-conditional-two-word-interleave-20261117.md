# K04: RECOVER-conditioned two-word interleaved metadata call

**Agent 47 | 17 November 2026 | bounded source-conditioned negative; no K04 recovery**

## Question

The stage-free MT analysis requires at least 428 hidden native outputs across the 127 ordinary packet gaps, while two CPython randbelow(3) metadata calls have an IID expected cost of about 339 outputs. A distinct, source-indexed possibility is that a CLASS=RECOVER job triggers one additional operation consuming two MT words between the CLASS and DEST samplers (or immediately after CLASS when DEST is sampled first).

This is a hypothesis about call topology, not a claim that the historical printer used random() or getrandbits(64). The two filler words are deliberately left unconstrained, so the test covers any operation that consumes exactly two native MT outputs.

## Frozen source and model

- Source: resources/evidence/print/spool-reconstruction.log, SHA-256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.
- Use the 128 ordinary rows 0–127 for metadata training. The observed ordinary set contains **35 RECOVER rows**.
- Exclude the selected PS-0417 ACK2 payload at source row 129 before building the source basis. Use the 132 intact payloads only; do not load the K04 mask, K04 commitment or canonical candidate.
- Retain the six baseline p950–p955 chronologies and the 164 source-compatible one-root ±1/±2 perturbations already defined by Agent44: **170 chronologies** total.
- Each payload is four consecutive little-endian MT19937 outputs. Each metadata sampler is CPython-style randbelow(3): consume a native output's top two bits; code 3 is rejection and codes 0–2 are accepted.
- Test a fixed global 3-way CLASS codebook and DEST codebook (all 3! × 3! = 36 pairs), both sampler orders, both current-row/next-row label bindings, and both first-sampler placements (at the first hidden word or after arbitrary unrelated prefix draws).
- If CLASS is first and its accepted code maps to RECOVER, skip exactly two unconstrained native words before the DEST sampler. If CLASS is second, require two words to fit after the accepted CLASS code and before the next payload. Other words between samplers must be possible rejection draws. Unrelated prefix/suffix draws remain allowed.
- Project each hidden word's top two bits from the source GF(2) basis. Any unresolved bit is allowed to be either value independently, deliberately creating an optimistic superset of possible native states.
- Fit the first **95** ordinary gaps; reserve the remaining **32** as holdout.

The finite test contains **170 × 36 × 2 × 2 × 2 = 48,960** configurations.

## Result

**Synthetic positive controls passed.**

| Baseline geometry | Source-compatible chronologies |
| --- | ---: |
| p950 | 35 |
| p951 | 28 |
| p952 | 25 |
| p953 | 21 |
| p954 | 31 |
| p955 | 30 |
| **Total** | **170** |

- **0/48,960** configurations fit all first 95 original ordinary gaps.
- The best configuration still contradicts **24/95** training gaps.
- No original configuration reached the 32-gap holdout.
- The synthetic positive control used a genuine seeded CPython random.Random(39117) stream, with a two-word getrandbits(64) call after accepted RECOVER when CLASS was first, and also tested DEST-first/CLASS-second with the two-word call after CLASS. Both planted schedules recovered the correct global codebooks and ordering with zero holdout errors (native stream lengths 947 and 952 respectively).
- **Authenticated K04 bits recovered: 0.**

## Interpretation

This rejects the specific RECOVER-conditioned, two-word interleaving under the tested 170 MT chronologies, static global codebooks, and sampler semantics. The failure is not explained by unresolved state bits: those were relaxed independently to either value, and the synthetic controls demonstrate that the test detects the planted schedule.

It does **not** prove that the historical printer had no interleaved calls. It does not test other conditional classes, other filler lengths, multiple or variable filler calls, per-row codebooks, multiple PRNG streams, a different generator, or a different physical copy stage. Those possibilities should not be enumerated without a new source-backed reason to choose them.

This result is distinct from Agent6's consecutive two-sampler test: it explicitly permits a two-word RECOVER branch between CLASS and DEST, or after CLASS in the reverse order. It is a conditional model exclusion, not an authenticated producer identification and not a K04 candidate.

## Reproduction

From the repository root:

~~~bash
python agents/agent47/k04_recover_conditional_two_word_interleave_sft.py
~~~

The script imports Agent44's source-pinned chronology and GF(2) machinery plus Agent6's optimistic top-two-bit projection. It checks the original spool SHA, withholds row129's payload, runs both planted positive controls, and leaves candidate.json, acceptance commitments, the verifier and all original evidence unchanged.
