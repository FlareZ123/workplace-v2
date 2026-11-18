# H-17 K04: full categorical-metadata packet-order sensitivity null

**Agent 6 | 18 November 2026 | narrow sensitivity check; zero recovered coupon bytes**

## Question

Agent17's same-day result, [metadata-stratified packet-order null](h17-k04-metadata-stratified-packet-order-null-20261118.md), permutes complete source packets within their original \`CLASS\`/\`DEST\` categories. This follow-up asks whether its 18/18 chronological orientation remains unusual when the permutation also preserves the two other categorical fields recorded in the spool log: \`STATE\` and \`ATTEMPT\`.

This is a sensitivity extension of that result, **not** a new discovery of the 25 recurrence identities and not the Critic's still-pending inlier/decoy stage-inference benchmark.

## Pinned source and method

- Unchanged source: \`resources/evidence/print/spool-reconstruction.log\`
- SHA-256: \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`
- 133 payload rows; selected \`PS-261003-0417\` attempt-2 \`ACK\` row index 129 is metadata-checked and excluded **before extracting or decoding its PAYLOAD field**.
- The remaining 132 immutable 16-byte packets are interpreted as four little-endian MT words and untempered. The source-only recurrence search independently reproduces 25 exact witness occurrences collapsing to 18 unique three-packet precedence triples; all 18 are forward in the actual chronology.
- Each null trial uniformly permutes whole packet identities only within identical \`(CLASS, DEST, STATE, ATTEMPT)\` groups. Packet bytes, word order, and the categorical metadata sequence are fixed. Job ID and timestamp are not permutation strata because they encode the chronology being tested; fixing them would trivialize the test.
- 200,000 seeded trials, Python \`random.Random(20261118005)\`. The standalone standard-library SFT is [\`k04_full_metadata_packet_null_sft.py\`](../agents/agent6/k04_full_metadata_packet_null_sft.py).

## Result

| Quantity | Observed |
| --- | ---: |
| Intact packets | 132 |
| Exact witness occurrences | 25 |
| Unique precedence triples | 18 |
| Original chronology forward | 18/18 |
| Full-metadata null trials | 200,000 |
| Mean forward triples | 7.446465 / 18 |
| Maximum forward triples | 16 / 18 |
| Trials with all 18 forward | **0** |
| One-sided 95% upper Monte Carlo bound for all-18 event | 1.4978549 × 10⁻⁵ |

Group-size histogram: \`{1: 3, 11: 2, 12: 2, 13: 1, 14: 1, 16: 1, 17: 1, 23: 1}\`.

The three singleton groups are the two \`REQUESTED\` attempts and the late \`RECOVER/bench/ACK/ATTEMPT=2\` packet at row 132. The 18-triple graph includes rows 131 and 132; row 132 is therefore fixed at its original final position under this stricter null, making its associated precedence relation automatically forward. Even with that conditioning, no trial orients all 18 triples forward. The late row 131 remains permutable within its 13-member full-metadata group.

For comparison, Agent17's \`CLASS/DEST\` null reported mean 7.417120, maximum 16, and 0/200,000 all-forward trials. Preserving \`STATE\` and \`ATTEMPT\` therefore does not remove the observed chronology enrichment. The small mean shift is descriptive, not a separate significance claim.

## Interpretation and limits

This result strengthens only the statement that the 18 packet-level numerical relations are unusually aligned with the recorded chronology under a categorical-metadata-preserving whole-packet permutation null. The 95% bound is a Monte Carlo bound for the all-18 event **under this particular null**, not a posterior probability that the historical printer used MT19937.

The recurrence equalities are not automatically authenticated ancestral stage edges: the known 31-bit hidden-predecessor alias can create exact numerical pseudowitnesses. This sensitivity test does not identify which witnesses are genuine, infer a unique global stage map, predict a held-out complete packet, or bridge to the selected physical coupon. It reads neither the K04 mask nor acceptance commitment and contributes **zero** K04 bits. The Critic's variable-gap inlier/decoy benchmark with frozen whole-packet holdouts remains a separate required discriminator.

No K04/K08 component, acceptance file, route, verifier, or canonical candidate was changed.
