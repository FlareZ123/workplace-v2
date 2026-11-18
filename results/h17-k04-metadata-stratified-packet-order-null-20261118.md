# H-17 K04: chronology survives frozen CLASS/DEST whole-packet permutation null

**Agent 17 | 18 November 2026 | source signal replication/extension; zero recovered coupon bytes**

## Independent question and source

Agent32 counted 25 exact native MT19937 whole-word identities in the 132 intact source printer packets, comprising 18 distinct three-packet dependencies, each forward in their actual spool chronology. Its exact all-packet uniform-permutation null probability for simultaneously orienting those 18 triples was 16/2,989,355,625. This follow-up asks whether the direction survives a stricter null in which the **recorded job-type metadata chronology remains fixed**.

Use only the original `resources/evidence/print/spool-reconstruction.log`, pinned SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Exclude the 18:02Z selected attempt-2 ACK row129 **before payload parsing**. The other 132 sixteen-byte packets are converted to little-endian native MT words via inverse tempering. Independently enumerate all equality links without requiring any chronology for the antecedent. Exactly 25 complete-word identities collapse to 18 unique packet triples, all with original parent packet earlier than both others.

## Discriminator and actual result

For each trial, permute **complete immutable 16-byte packet objects** among slots with the same `CLASS` and `DEST` tuple. The original ordered `CLASS/DEST` sequence, sample roles, per-packet internal word order and recovered word multiset are thereby fixed. For controls, separately preserve only CLASS, only DEST, or neither. Count a triple as forward when the permuted location of its parent packet precedes both companion locations. Each null has 200,000 independent seeded permutations from Python `Random(20261118004)`; regenerate the same seed separately for each mode.

| Conditional null | Complete permutations | Mean forward triples /18 | Maximum | All 18 forward |
| --- | ---: | ---: | ---: | ---: |
| **CLASS and DEST fixed** | **200,000** | **7.417120** | **16** | **0** |
| CLASS fixed | 200,000 | 6.453130 | 16 | 0 |
| DEST fixed | 200,000 | 6.136825 | 16 | 0 |
| Unstratified packets | 200,000 | 5.993635 | 15 | 0 |
| **Original observed chronology** | 1 actual sequence | **18** | 18 | 1 |

For the primary metadata-frozen null, the 200,000-trial histogram for forward-triple count 0..18 was `[18,150,1052,3743,10446,20432,30811,37682,36120,28098,17462,8828,3672,1137,297,48,4,0,0]`. The exact one-sided 95% binomial upper confidence bound for an independently simulated null probability given zero successes is `1 - 0.05**(1/200000) = 1.4978549e-5`. This is a **simulation confidence limit under the frozen-category permutation null**, not the exact all-packet probability from Agent32 and not a posterior probability that the historical device ran MT.

## Reproducer, interpretation and recovery boundary

[Standalone source-pinned SFT](../agents/agent17/k04_metadata_stratified_packet_null_sft.py) uses only the Python standard library; locally executed against the untouched user-supplied archive spool. It asserts all four precommitted forward sums/maxima and zero full-orientation successes. No protected service, target commitment, coupon, mask, or draft wording is inspected to discover the links.

The source MT-like word identities have a strong orientation in preserved packet chronology even when the observed CLASS/DEST distribution and within-packet structure are held constant. This independently strengthens Agent32's chronology result. It is still **not** evidence of the selected 18:02 physical coupon value or an authenticated copy-stage writer. The matching source packets do not observe any of the 128 selected K04 coupon bits under current producer models. K08 final caption remains absent. No new original acceptance hit, and all existing evidence/commitments/verifier/candidate remain untouched.

The next K04 recovery step requires a cross-stage producer or new selected-event original that predicts the entire 16-byte physical object. Another chronology null without a target-bearing construction would provide diminishing value.
