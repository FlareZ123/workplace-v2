# K04 historical MT-witness stage-fit and packet-holdout preflight

**Agent 43 | 19 November 2026 | bounded negative; no K04 bytes recovered**

## Question

Do the 25 exact MT19937-style recurrence witnesses in the nonselected printer packets support a source-blind monotone packet-stage map, and does that map identify stages for intact packet holdouts? This is the historical inlier/decoy preflight requested by the Critic, not a claim that every numerical equality is ancestral.

## Source and exclusion discipline

- Source: `resources/evidence/print/spool-reconstruction.log`
- SHA-256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- 133 payload rows. Source row 129 is metadata-checked as `PS-261003-0417 / ATTEMPT=2 / ACK / RECOVER`, then skipped before the payload substring is sliced, matched, or decoded.
- The 132 remaining packets are interpreted as four little-endian uint32 values and untempered. All 132 packets and all 528 words are distinct.
- Reproducer: [`agents/agent43/k04_historical_witness_stage_fit_sft.py`](../agents/agent43/k04_historical_witness_stage_fit_sft.py). Standard library only; no CI job.

## Frozen stage model

For each exact witness `(r,j,k,i,l,q)`, where the packet rows satisfy `r < k < l`, the MT recurrence implies:

- `S_k - S_r = 397 + j - i`
- `S_l - S_r = 624 + j - q`

The only packet-order prior is `S_(n+1) - S_n >= 4`, reflecting at least the four captured words per packet. No upper gap, class-dependent hidden-draw model, or post-hoc stage map is fitted. The 25 witness relations are all retained unless the resulting difference-constraint system is infeasible.

## Historical fit

The source-pinned reproducer independently recovers **25** chronological exact witnesses.

| Measure | Result |
|---|---:|
| Exact witnesses | 25 |
| Monotone stage graph feasible | yes |
| Equality-graph components (excluding selected row 129) | 96 |
| Selected row 129 stage interval, with row 0 anchored at 0 | **916–971** |
| Single-edge deletions that remain feasible | **25/25** |

The graph is feasible but highly disconnected. The selected row's interval contains 56 integer positions; it is not a unique stage. Because the complete 25-edge graph is feasible, removing any one edge also leaves a feasible graph. The consistency-only maximum-consensus rule therefore cannot identify a unique decoy among the historical witnesses. This does not prove that any particular witness is false; it shows that the planted synthetic one-edge-rejection success is not a general classifier for this source.

## Whole-packet holdout stage test

Each intact ordinary packet was held out in turn **before** witness discovery; its four words were absent from the fit. Row 0 is the coordinate origin and row 129 is the intentionally excluded selected ACK2, leaving 131 holdouts.

| Measure | Result |
|---|---:|
| Holdout fits feasible | 131/131 |
| Holdout stages uniquely determined | **0/131** |
| Finite two-sided stage intervals | 128/131 |
| Interval width, min / median / mean / max | **55 / 62 / 69.87 / 141** |
| Rows with no finite upper bound | 53, 83, 132 |

The training witnesses do not determine a unique stage for any intact packet holdout. This is a stage-identifiability result, not a packet-byte prediction; the model cannot make a unique whole-packet prediction from these stage constraints.

## Source-preserving controls

Each control used 96 deterministic trials with Python `random.Random`; the seeds are fixed in the reproducer. Whole packets were permuted while row positions and metadata strata were preserved.

| Control | Mean witnesses | Median | Range | Trials with ≥25 | Feasible stage graphs |
|---|---:|---:|---:|---:|---:|
| Whole-row shuffle | 8.83 | 8 | 2–18 | 0/96 | 3/96 |
| CLASS × DEST shuffle | 10.66 | 11 | 5–18 | 0/96 | 0/96 |
| CLASS × DEST × STATE shuffle | 9.91 | 10 | 2–18 | 0/96 | 2/96 |

None of the feasible shuffled graphs yielded a finite two-sided interval for selected row 129. These are deterministic empirical controls, not calibrated p-values. The original 25-witness graph is strongly chronology-enriched relative to these controls, but the enrichment does not supply a unique global stage map.

## Decision and limits

This closes the **simple exact-witness + monotone-minimum-gap fit** as a K04 recovery route. It preserves the evidence that the spool contains a real chronology-dependent MT-style numerical signal, while showing that the historical witness graph cannot classify its own edges or locate held-out packet stages uniquely.

The separate [oracle-stage whole-packet result](h17-k04-inlier-decoy-oracle-wholepacket-20261118.md) is an even stronger conditional bound for the maximal-state linear MT model: with the p951 stage positions supplied, it predicts **0/132** complete intact packets and fixes **0/128** selected-coupon bits. That result is conditional on the p951 geometry, not an authenticated historical stage map; it does not exclude a source-attested shorter initializer or an independent physical-copy constraint.

**Research consequence:** do not expand this into arbitrary gap priors, generic PRNG families, or another stage-only sweep. A K04 advance now requires a source-authenticated initializer/consumption rule or an independent original physical ESC-N coupon/rendered-copy record. No K04/K08 component, candidate, acceptance commitment, route, verifier, or original evidence was changed. Six components remain PASS; K04 and K08 remain missing; combined recovery remains INCOMPLETE.
