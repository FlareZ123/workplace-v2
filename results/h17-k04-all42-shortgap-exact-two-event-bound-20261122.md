# K04: all-42 original MT witnesses force at least two short printer event gaps

**Agent 8 | 22 November 2026 | Exact source-stage obstruction; original K04/K08 unresolved.**

## Constructive source-only question

Agent 4's [four-doublet obstruction](h17-k04-four-doublet-min7-schedule-obstruction-20261122.md) proves that four intact MT19937 two-word recurrence anchors cannot come from one producer consuming seven or more native words at **every one of 32 original event gaps**. We asked whether allowing just one short gap repairs the contradiction when **all 42 independently matched original scalar native MT recurrence witnesses** are imposed.

The original 133-line spool is SHA-256-pinned at 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. The selected 18:02Z PS-261003-0417 ACK2 row129 is identified from metadata; its disputed PAYLOAD is skipped before hexadecimal parsing. The 42 source arithmetic relations comprise 25 exact native fullword triples and 17 firstword 31-bit triples with a single missing predecessor MSB. No original acceptance hash was used to select them.

The region consists of **32 original ACK gap row indices**: 12–31, 65, and 115–125. Define a short event as consuming at most six native words between one row start and the next. All ACK rows must consume at least four words; REQUESTED rows elsewhere may consume zero.

## Source-stage exact integer computation

Each recurrence triple (r,k,l,p,i,q) imposes the necessary row-start stage equalities:

- S[k] minus S[r] equals 396 + p minus i;
- S[l] minus S[r] equals 623 + p minus q.

For each proposed set of short events, force 4–6 native word draws at those rows, 7–100 at other rows in the 32-event region, and source ACK 4–100 / REQUESTED 0–100 elsewhere. Every condition is an **integral difference constraint**. It is feasible if and only if its directed graph has no negative-weight cycle, so exact standard-library Bellman–Ford checks prove feasibility without heuristic optimization, numeric rounding or SHA-guided search.

[Reproducer: original-source 42-witness short-gap SFT](../agents/agent8/k04_mt_all42_shortgap_sft.py).

| Source recurrence assumptions | Allowed short events in the 32-gap region | Exact integer stage result |
|---|---|---|
| 25 fullword witnesses | 0 | Infeasible |
| 25 fullword witnesses | Only row12 | Feasible |
| All 42 fullword + firstword witnesses | 0 | Infeasible |
| **All 42 witnesses** | **Any one of 32** | **Infeasible for all 32** |
| **All 42 witnesses** | **Any two of 32** | **435 of 496 pairs feasible** |

The 435 feasible exactly-two-short pairs are **every pair drawn from 30 rows** (14–31, 65, and 115–125). In particular, rows12 and13 cannot be exceptions when there are exactly two. This does not show that either is always long if three or more rows are short. One exact feasible two-exception integer stage assignment consumes four native words at rows65 and118 and at least seven in the other 30 region gaps.

**Consequence:** Under the all-42 one-stream native MT model, at least two of these 32 events must consume six or fewer native words. This strengthens the earlier one-short-event bound but leaves 435 distinct minimal stage choices, so no particular real print gap is established.

## Stronger full-original-ACK bound: nine mandatory short events

The 32-event region is only part of the printer stream. Extending the same all-42 original stage equations to **all 130 original ACK rows with successor rows** yields a stronger, globally minimal exception count. Set each event's native gap to 4–100; require at least 7 whenever its binary short-event indicator is zero and allow 4–6 whenever the indicator is one. Other REQUESTED events may consume zero. Minimize the sum of all 130 binary indicators with **exact mixed-integer linear programming**, integrality and 0.0 optimality gap. These are the same row-stage difference equalities as the source-pinned Bellman–Ford test; no sample data or original K04 hash informs the optimization.

| Original source MT witnesses | Exact minimum ACK gaps with 4–6 native draws |
|---|---:|
| Original 25 exact fullword witnesses | **5 of 130** |
| All 42 fullword plus partial-firstword witnesses | **9 of 130** |
| All42, additionally requiring selected ACK2 row129 itself short | **9 of 130** |
| All42, additionally requiring selected ACK2 row129 long (at least 7) | **10 of 130** |

One all42 optimal **stage-feasible** assignment has short original ACK indices **33,39,84,87,121,124,126,129,131**, with every other ACK row using at least seven native words. This example is not proven to fit all 528 actual source packet words as one global MT internal state; a minimal equality model only satisfies the source-derived 42 arithmetic witness constraints. It is a constructive *stage-bound witness*, rather than an authenticated printer explanation.

The independent [source-pinned global ACK MILP SFT](../agents/agent8/k04_mt_global_ack_shortgap_milp_sft.py) uses NumPy and SciPy/HiGHS, enforces integer stage and binary indicator variables, asserts exact original source equalities, and requires optimality gap zero. It has been run locally and [passed the complete source-SFT GitHub Actions workflow 45060274595](https://github.com/FlareZ123/workplace-v2/actions/runs/45060274595) with the original source unchanged. The global 9/10 bound makes any blanket seven-native-word-per-ACK scheme with only a few exceptional events implausible under the all42 MT model, and illustrates why the true generator gap rule must be established from independent printer evidence before predicting the selected physical coupon.

## Acceptance and limitations

All 42 relations are source-observed arithmetic equalities. Some may be accidental coincidences, since the actual physical printer writer has not been established. The known published p951 full-source MT chronology satisfies all 42 and all 528 intact 32-bit original source words and has many six-output gaps; the new bound therefore does not imply universal original MT inconsistency. It also does not recover the selected physical ACK2 coupon. The only all-42 selected direct native donor relation aliases the earlier unacknowledged REQUESTED1 firstword; see [full target-stage analysis](h17-k04-stage-graph-conditional-full-coupon-20261122.md).

This conditional theorem rejects printer models allowing at most one such short event, while identifying no authentic K04 byte or K08 keeper phrase. A genuine source-defined producer and an independent complete-packet holdout are still required. Original canonical source, route, acceptance, verifier and six passing components remain unchanged; REC8/1 remains incomplete.
