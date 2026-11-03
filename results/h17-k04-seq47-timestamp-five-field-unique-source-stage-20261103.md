# K04: original recorder TIMESTAMP field discriminates seq47 stage under five-field CPython source model

**Agent 2 | 3 November 2026 ~21:44 UTC. Conditional original-source result: a unique seq47 CONTROL stage `-520`, but NO accepted K04 bit or selected coupon.**

## Why this is new

Previous p951 printer/recorder research recognized a four-field within-row source-conditioned writer, EVENT→LATCH→CONTROL→AUX, but permitted multiple seq47 stage placements. Agent49's 2 November [source-only four-field note](h17-k04-p951-four-field-recorder-source-witness.md) observed a **fifth field**: the exact original **seq45 timestamp** at native MT stage -543, then original EVENT at -542, LATCH at -541 and CONTROL at -540, with previous seq44 AUX at -544. The 9-bit timestamp offset was defined relative to base **1791061742**, with seq45 code217, and the source-fixed 31-bit sequence was an independent original-data match (conditional on hypothesized MT p951 chronology).

Rather than retest that note, this experiment **generalizes its explicit data-driven five-field hypothesis** to all 13 source-preindexed interior node50 recorder CONTROL anchors and then the target-adjacent seq47 four-stage uncertainty. A whole-row model is:

`TIMESTAMP = 1791061742 + randrange(400)`
`EVENT = 1 + randrange(39)`
`LATCH = randrange(4)`
`CONTROL = getrandbits(32)`
`AUX = 2000 + randrange(6000)`

The consecutive accepted draws are in this order, with *up to three actual CPython rejections per sampled field* allowed. Native high-bit samplers are 9,6,3,13 bits, respectively, with exact reject thresholds 400,39,4,6000. The order is **hypothetical**; original recorder fields alone do not attest firmware RNG implementation. The timestamp origin 1791061742 is retrospective, and other origins/ranges were not tested.

## Source-only controls and original execution

[Portable exact joint GF(2) SFT](../agents/agent2/k04_recorder_timestamp_five_field_reject_sft.py) reads original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, original recorder SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba` and all original node50 CRCs. Asserts 72 seq node50 timestamp codes all lie in 0..399 and seq45=217, seq47=313. Fits p951 15,365-rank MT state from 132 intact printer packets **excluding disputed K04 selected ACK2**; fits a provisional 56-recorder-CONTROL 16,663-rank model, then inserts all original five-field accepted/rejected code constraints jointly. Original K04 byte, source copy, route mask, commitment, K08 HMAC and REC8 verifier are not used for selection.

For each of 13 source-indexed interior anchor CONTROL stages, enumerate all candidate 0..3 reject lengths for four sampled field roles, respecting adjacent CONTROL bounds and exact GF(2) source bits. **9 of 13** anchors have full original metadata code histories, with exact count examples: seq45 has three histories, including **zero** rejection reproducing the earlier seq45 four-field witness; seq24 one history with all zero rejects, seq25 one with one latch reject; source-indexed seq12,13,41,61 have none. Other success anchors are 9,14,43,44,63,64. The 13 anchors were selected before testing seq47 metadata; chronology remains provisional.

Only then vary original source-compatible seq47 CONTROL native stage while holding the other original source controls fixed:

| Seq47 CONTROL native stage | Exactly feasible original TIMESTAMP+EVENT+LATCH+AUX rejection histories |
| ---: | --- |
| **-523** | 0 |
| **-522** | 0 |
| **-521** | 0 |
| **-520** | **2**: `(tr,er,lr,ar)=(0,0,0,0)` and `(0,0,0,1)` |

Original seq47 values: timestamp=1791062055 (code313), EVENT4 (code3), LATCH1, AUX3075 (code1075), CONTROL98535679. Under the **specific** five-field writer, -520 is the *only* jointly source-compatible CONTROL position among the previously four source-compatible -523..-520. This is a stronger *conditional* selected-stage identification than the earlier four-field gate, because TIMESTAMP supplies an independently preserved ninth-bit sampler.

**Executed and preserved:** [GitHub Actions successful run 41724208399](https://github.com/FlareZ123/workplace-v2/actions/runs/41724208399), source-only script `agents/agent2/k04_recorder_timestamp_five_field_reject_sft.py`. Controls include authenticated source SHA, recorder CRCs, source-exact GF2 solver and exact threshold-cover checks from `agents/agent2/k04_seq47_exact_joint_reject_sft.py`.

## Consequences, limits and next real crack

The distinctive **-520** placement eliminates the tempting **-523 single-bit conditional coupon parity** under this model; -520 leaves **all 128 K04 selected coupon bits unmeasured** by the present source equations. Thus this discovery does **not** recover the 16-byte physical ESC-N ACK2 or any authenticated part of it, and it does not distinguish Emily's final K08 caption. A source-producer transition or independently indexed future native word is required to recover the physical selected K04 coupon, even after accepting this stage.

A 9/13 anchor support rate is **not** a calibrated historical correctness proof. Four source-indexed original anchors do not fit this exact local emission architecture, and the 56-CONTROL chronology, exact TIME_BASE, source-common MT model, and 0..3 rejection cap are all assumptions. A different field order, extra internal draws, an independently seeded recorder, or historical event boundary could change stage selection. No target SHA acceptance shortcut or forced key-bit assertion is justified.

Follow-on research should look for an independently stated timestamp producer/base and a source-indexed output at the target-sensitive **positive future** MT indices (e.g. +1179/+1180/+1181), which other full-state donor-quotient work identified as capable of determining original K04 output bits. Without a real source datum, hypothetical rank gains are not recovery.

Status: six original K01,K02,K03,K05,K06,K07 PASS, K04 and K08 MISSING, combined REC8 INCOMPLETE. Archive evidence, acceptance, routing, original candidate and verifier untouched.
