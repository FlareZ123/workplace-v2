# K04: original TRP2 four-quartet 227-output future-donor completion is finite and fails the original commitment

**Agent 19 | 2 November 2026 ~19:28 UTC | New target-bearing conditional candidate attack; no K04 recovery.**

## New proposed completion route

Agent32's [p951 227-pair target window](h17-k04-p951-227-pair-target-window.md) proved an exact recurrence attack: two full MT19937 state words at positions `t+397` and `t+624` reveal the mixed 32-bit antecedent `X[t].MSB || X[t+1].low31` by inverse-twisting their XOR. For `t=950..953`, **four paired 32-bit donor observations** from each of the two consecutive future windows supply **127/128** state bits of the selected four-word K04 coupon at `t=951..954`. Only `X[954]`'s MSB remains to try as 0 or 1. The first pair also predicts `X[950]`'s MSB, which the surviving **unselected** printer row128 records and thus supplies a one-bit rejection gate.

The original `trip-recorder.raw` has an unusual, independently numbered **four-quartet** cohort in node49/event82, sequences 200..203, 300..303, 900..903 and 990..993, all four bytes each. Unlike v1 Agent8's already completed *literal four-control concatenation* search, this experiment treats two disjoint original source quartets as the **future MT recurrence inputs** and algebraically computes previously unseen selected native outputs. It changes the mathematical source-to-candidate mechanism and uses the full target-bearing 227-output donor geometry. It hypothesizes (without source attestation) that one quartet could occupy source positions 1347..1350 and a different quartet 1574..1577. These positions are chosen from the independent MT recurrence, not fitted by the acceptance hash.

Under little-endian state untempering (the previously observed cross-source orientation), source suffix ordering has a natural group-level interpretation. To allow the original shuffled recorder-storage order, test both orders of source quartets and all **24** permutations *within each*.

## Original source and exact result

Original recorder SHA-256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`; printer spool SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Unselected row128 native final 32-bit word fixes predecessor bit31 to **1**. No selected row129 bytes enter construction or ranking. The original K04 route mask and SHA256 commitment are read **only after** all complete native coupon candidates have been generated.

| Distinct source-cohort model | Original result |
| --- | ---: |
| Natural sequence-order ordered quartet pairs | 12 |
| Natural sequence-order pairs surviving row128 predecessor bit | **8** |
| Ordered quartet pairs with 24 × 24 within-group permutations | **6,912** |
| Permuted pair assignments passing original predecessor bit | **3,888** |
| Full coupon completions per surviving assignment (last MSB) | 2 |
| Unique 16-byte complete candidate coupons after symmetries | **3,888** |
| Original K04 SHA256 commitment matches after XOR with original route mask | **0** |

The 900-series quartet has the previously documented uniformly **bad recorded CRC**; it is deliberately retained for this exploratory source-connection hypothesis, and **never** used as a K05 accepted record. Among only the three CRC-good quartets there are six source-order cohort pairings; allowing the CRC-bad group expands the already bounded conditional hypotheses, without an invented donor field.

**End-to-end synthetic positive:** four independently seeded actual CPython MT19937 streams generated at least 1578 native outputs. Withhold selected outputs 951..954; supply source positions 1347..1350 and 1574..1577; calculate the four inverse-twists plus the known original predecessor bit and the two final-bit options. In **all four** controls the true withheld full four-word native coupon appears in exactly one of the two completions. Full original-case SFT asserts the 12/8/6912/3888/3888 counts with original source hashes and returns no K04 candidate passing the original acceptance.

[Source-pinned standalone SFT](../agents/agent19/k04_future_trp2_quartet_pair_sft.py) (Python standard library only).

## Recovery implication and provenance limits

The selected coupon would be completely recoverable from just two *real* independently indexed four-control runs 227 draws apart, plus the known preceding printer bit and a single brute-forced terminal MSB. This is a stronger concrete hypothetical K04 full-candidate pipeline than isolated matching controls or direct source concatenations. **None of the four original recorder cohorts is historically attested as occupying those two future printer-generator windows.** The no-match closes only the explicitly tested quartet-to-window assignment family. It does not contradict Agent32's general future-pair mechanism or rule out unknown, differently indexed original donors. The p951 common-MT producer itself remains a mathematical original-spool-compatible chronology with existing metadata-stage counterevidence.

Actual independent K04 selected bytes recovered: **0/16**; original K04 acceptance still **NO_MATCH** for the retained copied ACK; K08 final caption still absent. Six established components PASS, original REC8 combined **INCOMPLETE**. Do not promote any of the 3,888 speculative coupons to the key.

Nearest prior art: [v1 Agent8's direct four-token recorder mosaic](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-trp2-four-word-donor-permutations.md), and [the earlier prospective three-/future-donor algebra](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-target-leverage-constellations.md). Neither used two original labeled four-control cohorts as 227-apart future donor pairs to form complete candidate coupons under the original acceptance.
