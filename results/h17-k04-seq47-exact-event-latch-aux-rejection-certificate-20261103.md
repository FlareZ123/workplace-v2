# K04: exact coupled EVENT/LATCH/AUX source-stage cut for the seq47 target-adjacent MT hypothesis

**Agent 2, 3 November 2026, 21:17 UTC. Original components recovered: zero.** This is a **conditional source-model discrimination** against a proposed CPython MT19937 recorder writer. It proves no original selected coupon bit and does not change the six-PASS / K04+K08-missing / combined-INCOMPLETE archive result.

## New mechanism and why it matters

The established source-fitted printer GF(2) basis has rank 15,365. A provisional 56-row recorder CONTROL chronology produces four complete original-source-compatible choices for node50 recorder seq47's CONTROL native stage: **-523, -522, -521, -520**. Only -523 creates a 1-bit conditional parity of the *unseen* selected K04 coupon. Earlier Agent8 work checked the immediately preceding 3-bit latch for a particular stage; Agent47 then introduced separate EVENT and AUX source-bit rejection-range screening. The present experiment strengthens that by enforcing **all accepted and rejected field bits simultaneously** in the same exact source-GF(2) state. It never fits the selected printer buffer, its route mask, K04/K08 commitments or known K04 parity.

Proposed field-producer sequence for one recorder row (the source does **not** attest this writer): EVENT = 1 + CPython randrange(39), LATCH = randrange(4), CONTROL = one complete 32-bit word, AUX = 2000 + randrange(6000). The three calls use native tempered word high 6, high 3 and high 13 bits, respectively, with rejected draws until the corresponding code is in range. Original seq47 independently records EVENT **4** (accepted code 3), LATCH **1**, AUX **3075** (accepted code 1075). No further draw may intervene *between the accepted LATCH and CONTROL* in this proposed ordering. Neighboring CONTROL stages are seq46 **-531**, seq48 **-512**.

## Exact feasibility algorithm

The [source-pinned, standard-library SFT](../agents/agent2/k04_seq47_exact_joint_reject_sft.py) imports existing exact printer and 56 CONTROL state-equation builders, inserts every observed field bit as a GF(2) equation, detects contradictions with reversible Gaussian elimination and enumerates **disjoint binary-prefix covers** of rejected codes. For each `k,threshold`, a constructor independently verifies that its patterns cover each integer in `0..2^k-1` exactly once iff it meets the threshold: event rejects 39..63 have **3** prefix cubes, latch rejects 4..7 have **3**, AUX rejects 6000..8191 have **7**. Thus it tests inequalities rather than approximating rejects by an arbitrary bitmask. The first stage also checks exact consistency for **every** accepted EVENT/LATCH/AUX triple that could fit between neighboring CONTROL records, irrespective of how many rejects produced that spacing.

Original evidence pinned by existing source assertions: spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, recorder SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`, each node50 CRC valid, all 56 CONTROL readings preserved. The original sample selected printer row129 is not fitted. Synthetic correctness checks include all-code exhaustive prefix-cover membership (13-bit case 8,192 possible codes) and successful exact joint witnesses for two original-source-compatible *hypothetical* field-stage histories.

## Executed results

| Seq47 CONTROL stage | Source+CONTROL rank | All possible joint accepted-field placements within neighbor boundaries | Exact feasible histories (each of EVENT/LATCH/AUX with 0..2 rejects) |
| --- | ---: | ---: | ---: |
| **-523** | 16,663 | **0** | **0** |
| **-522** | 16,664 | 4, all requiring event accept at -530 | **0** |
| **-521** | 16,664 | 6 | **3** |
| **-520** | 16,664 | 6 | **6** |

Two exact impossibility certificates give stronger conclusions than the 0..2-rejection table:

1. **-523:** last accepted LATCH must be high3 bits at native stage **-524**, and the exact source state fixes bits inconsistent with original LATCH=1 (Agent8 already identified this conflict). Thus *any* number of earlier rejected latch draws fails under the immediate-predecessor producer.
2. **-522:** among all accepted-field triples only EVENT accepted at native stage **-530** allows its code3, given the other original constraints and neighboring CONTROL bound. This would require **six** rejected latch draws at stages -529..-524 before accepted LATCH at -523. After inserting the exact EVENT code3 at -530 into the *same* original source state, the high 3 bits at the first mandatory reject stage **-529 are fixed to (LSB-first 1,1,0), code 3**. Rejection requires code at least 4. Every possible AUX-after-control history therefore fails. The SFT also explicitly tests all four AUX accepted placements -521..-518 with all six mandatory latch rejects; all are UNSAT, with just four prefix expansions apiece.

Stages -521 and -520 admit simultaneous original EVENT/LATCH/AUX values with **zero** rejects; multiple compatible histories remain. Source-side controls do not distinguish those two stages and neither constrains any target K04 bit in the prior exact quotient calculation.

Original-source execution: [GitHub Actions run 41720344723](https://github.com/FlareZ123/workplace-v2/actions/runs/41720344723), commit `cc57eaf484504f5c5deb0197fd208acf107e9763`, job success. Earlier [run 41720136908](https://github.com/FlareZ123/workplace-v2/actions/runs/41720136908) independently printed the full 0..2-rejection and accepted-placement counts; the final run added a one-stage 3-bit certificate.

## Limitations and high-value next step

The **writer architecture is unverified**. The exact *no-rejection* version of this field model is compatible with only **7/15** source-preindexed anchor rows and **12/40** other placed recorder rows; some could require actual rejected draws or an unrelated producer. Exact target-bearing -523 is ruled out **only** if the assumed event/latch/control/aux sequence and immediate-predecessor latch really produced seq47. An unrecorded field draw or different stage assignment outside this source-fitted chronology can change the verdict. The bit at the conditional -523 stage must **not** be represented as recovered from historical evidence.

Practical priority: obtain or infer the recorder's actual field draw order/rejection rule from independent original preserved rows or producer documentation before upgrading the stage cut. A stronger source calibration must show the model works without retrospective stage and label selection. Until then, pursue an independent physical selected ACK2 source or the authentic Emily final caption. This scoped exact source contradiction is a research deliverable, **not** a full K04 reconstruction or a reason to expand unconditional random generator name searches.
