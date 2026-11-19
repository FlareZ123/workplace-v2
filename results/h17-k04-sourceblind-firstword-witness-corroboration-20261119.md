# K04: source-blind firstword-witness corroboration and packet-shuffle null

**Agent 50 | 19 November 2026 | source-only recurrence analysis; no coupon recovered**

## Question

Do the 17 source-row firstword (31-bit) recurrence relations add coherent stage information to the 25 fullword relations, without importing the p951 chronology? Are the resulting 42 chronological relations more than packet order would produce when the exact intact packet multiset and job metadata are preserved?

This extends, rather than repeats, the earlier 25-fullword-edge historical stage-fit preflight. It tests the additional firstword relations against the fullword anchor graph and uses 200,000 whole-packet permutations per metadata-preserving null.

## Frozen source and exclusion

- Input: `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- 133 spool rows, 132 intact 16-byte packets.
- The selected PS-261003-0417 attempt-2 ACK at row 129 was identified by its job/attempt/state/class fields and **excluded before its PAYLOAD field was parsed**.
- No p951 stage vector, K04 mask, K04 acceptance digest, candidate file, verifier, or selected ACK bytes were read.
- Each intact packet was split into four little-endian 32-bit words and inverse-tempered. The recurrence relation uses the native MT19937 397/624 offsets; when the source word is lane 0, the preceding word's MSB is unobserved, so both possible predecessor-MSB values are considered.

## Original source result

The source chronology yields **42 distinct recurrence relations**:

| Relation type | Count | Meaning |
| --- | ---: | --- |
| Fullword (source lane 1–3) | **25** | The predecessor word is in the same packet; the full 32-bit recurrence equation is testable |
| Firstword (source lane 0) | **17** | The preceding word is outside the packet; one predecessor MSB is unknown, leaving a 31-bit relation |
| **Total** | **42** | All are distinct relation tuples |

The 25 fullword relations alone form a monotone stage-feasible graph with 96 equality components and a selected-row start-offset interval of **916–971**. Adding the 17 firstword relations gives:

- **83** equality components;
- a still-feasible monotone stage graph;
- a selected-row start-offset interval of **917–971**;
- row 129 still isolated in the exact-equality graph.

Thus the firstword relations join 13 additional components and tighten the lower bound by one, but they do not identify a unique selected-row stage.

### Firstword inlier/decoy assessment

Using only the 25 fullword relations as anchors, the 17 firstword relations have the following graph-implied offset status:

| Assessment against fullword anchors | Count |
| --- | ---: |
| Both expected destination-stage offsets implied by the fullword graph | **10** |
| Exactly one destination-stage offset implied | **1** |
| Neither destination-stage offset implied | **6** |
| Contradictory offsets | **0** |

These are graph-implied offsets, not independent confirmations. A dependence audit finds that only **3/10** both-offset relations remain supported after deletion of any single fullword anchor; the other **7/10** each depend on one particular fullword anchor. **0/10** remain supported when all anchors touching any of the firstword relation's three packet rows are excluded. Only **3/10** remain supported when exact recurrence input words are disjoint. A fullword anchor at source lane j uses both source words at lanes j−1 and j; each of the seven fragile anchors therefore reuses the firstword relation's lane-0 source word as the predecessor of its lane-1 anchor.

The seven single-anchor dependencies are especially revealing: each is paired with a fullword relation over the **same three packet rows**, with all three recorded lane indices advanced by one. Because the fullword recurrence also consumes the preceding source lane j−1, each such anchor shares the firstword relation's lane-0 source word. The row/lane tuples (0-based) are:

| Firstword relation | Necessary fullword anchor |
| --- | --- |
| (3,0) → (56,2) → (86,1) | (3,1) → (56,3) → (86,2) |
| (13,0) → (67,1) → (97,2) | (13,1) → (67,2) → (97,3) |
| (15,0) → (69,0) → (99,2) | (15,1) → (69,1) → (99,3) |
| (31,0) → (83,2) → (114,0) | (31,1) → (83,3) → (114,1) |
| (38,0) → (91,2) → (121,2) | (38,1) → (91,3) → (121,3) |
| (41,0) → (94,2) → (125,0) | (41,1) → (94,3) → (125,1) |
| (45,0) → (98,2) → (132,2) | (45,1) → (98,3) → (132,3) |

The three firstword relations that survive every single-anchor deletion **and** exact recurrence-input-word exclusion are (8,0)→(62,0)→(92,1), (12,0)→(66,0)→(96,1), and (42,0)→(95,0)→(126,1). Even these remain packet-overlapping; none has row-disjoint support. The predecessor word whose MSB distinguishes each 31-bit alias is absent from the observed words in the relevant equality component. **0/17** predecessor MSBs are independently observed, even after all 42 relations are included. No historical relation is contradicted by the monotone graph, but the six uncorroborated relations remain unclassified rather than being promoted or rejected.

## Whole-packet permutation controls

The nulls preserve the **exact multiset of intact 16-byte packets**, including each packet's four-word internal order, and permute whole packets only among slots sharing the listed metadata. The selected row remains excluded. Potential recurrence triplets are generated once from the fixed word multiset; each trial changes only their chronological packet positions.

| Control | Trials | Group sizes | Mean relations | P95 | Maximum | Maximum fullword / firstword | Trials with 42+ |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| CLASS + DEST fixed | 200,000 | 23, 17, 16, 14, 14, 13, 12, 12, 11 | 17.151 | 25 | **37** | 23 / 15 | **0** |
| CLASS + DEST + STATE + ATTEMPT fixed | 200,000 | 23, 17, 16, 14, 13, 12, 12, 11, 11, 1, 1, 1 | 17.385 | 25 | **37** | 24 / 16 | **0** |
| Original chronology | 1 | unchanged | **42** | — | **42** | **25 / 17** | **1** |

Neither 200,000-trial null reproduced the observed total of 42; the maximum was 37 in both. The one-sided 95% binomial upper bound after zero exceedances in 200,000 trials is **1.4979×10⁻⁵** for the probability of reaching 42 under each specified permutation null. This is a Monte Carlo bound for these frozen controls, **not** a formal probability that the historical writer used MT.

The secondary statistic of at least 10 firstword relations with both offsets supported occurred in 21/200,000 CLASS+DEST controls and 19/200,000 full-metadata controls. It is not as discriminating as the total relation count and is not presented as an independent significance test.

## Interpretation and recovery boundary

**Computational result:** The original packet chronology is substantially more aligned with this MT recurrence operator than either whole-packet metadata-preserving shuffle. Ten of the 17 partial firstword relations have offsets implied by the fullword graph, but the dependence audit shows only 3/17 remain both-offset supported after excluding anchors that reuse exact recurrence-input words; none has row-disjoint support. The principal evidence is the 42-relation count exceeding both 200,000-trial null maxima.

**What this does not establish:** It does not authenticate a particular MT implementation, determine a unique historical stage map, independently validate the graph-implied firstword offsets, validate the 17 unknown predecessor MSBs, or predict any selected physical coupon bytes. The selected row 129 is absent from the recurrence graph; its start offset remains a 55-position interval, and its 128 coupon bits remain unobserved. This is not a K04 candidate or acceptance hit.

The earlier [oracle-stage whole-packet benchmark](h17-k04-inlier-decoy-oracle-wholepacket-20261118.md) shows why even a supplied stage map is insufficient under the maximal linear MT model: the selected coupon remains 128 bits unconstrained. The earlier [historical stage-fit preflight](h17-k04-historical-witness-stage-fit-20261119.md) used the 25 fullword edges; this report adds the 17 firstword-edge corroboration and a much larger whole-packet null for the resulting 42-relation statistic.

## Next action

Do not widen generic MT/PRNG or sampler grids. The remaining K04 path needs a selected-event discriminator that can constrain the complete 16-byte object: native PS-0417 attempt-2 REQUESTED/ACK queue journal, driver/renderer output, physical coupon/media witness, or an independently authorized AX-7782 native object and manifest that explicitly bind to the selected PS-0417 stage. Use the existing read-only intake tooling if such a local original is voluntarily supplied.

## Reproducer

[Source-pinned SFT](../agents/agent50/k04_historical_inlier_decoy_sourceblind_sft.py) uses only the Python standard library, asserts the original source SHA and row-129 exclusion, and reproduces both 200,000-trial controls with fixed seeds. The original evidence, canonical candidate, acceptance commitments, and verifier were not modified.
