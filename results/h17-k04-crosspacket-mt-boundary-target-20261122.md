# K04: cross-packet MT boundary witnesses, complete coupon and stage transfer

**Agent 8 | 22 November 2026 | A new source-observable recurrence family; complete K04 remains unresolved.**

## Direct reconstruction test

Earlier work tested MT19937 recurrences using two consecutive words **inside the same retained 16-byte printer packet**. This experiment tests a different conditional geometry: the four native words of one printer row are immediately followed by the first word of its *next intact row*. An exact native MT twist at this packet boundary can combine with a later intact packet to predict a third packet. Such a boundary requires **zero hidden draws between the two source packets**; the exporter does not attest that schedule.

The original source is SHA-256-pinned at resources/evidence/print/spool-reconstruction.log (7d71d8be...f3841b6083). The selected 18:02Z PS-261003-0417 / ACK2 / RECOVER row129 is identified from metadata; **its disputed payload is not decoded**. The original route mask and full K04 acceptance commitment are unchanged.

For each triple of intact source rows r < k < l, untemper the 32-bit packet words and calculate:

    native[l][q] = native[k][i] XOR twist(native[r][3], native[r+1][0])

Retain exact historical witnesses, allowing every lane i,q=0..3. The resulting new boundary witnesses under little-endian forward words are:

| Source r,k,l | Partner lane i | Destination lane q |
|---|---:|---:|
| 3,57,87 | 3 | 3 |
| 12,67,97 | 1 | 2 |
| 13,68,98 | 1 | 3 |
| 33,86,116 | 2 | 3 |
| 40,94,125 | 2 | 0 |
| 43,97,130 | 2 | 3 |

The original file also has 25 intra-packet witnesses, reproduced independently before this extension. Across the four whole-packet views, boundary witness counts are **6 little-forward, 2 little-reverse, 0 big-forward, 0 big-reverse**. On 1,000 seeded global shuffles preserving complete packets and the excluded target row, little-forward boundary witnesses averaged 2.744; 37/1,000 produced at least six. This is a **conditional descriptive null**, with source-view and exploratory selection effects, not a historical producer probability.

## Complete original K04 candidates

Transfer each witnessed source-relative row offset to the selected raw row129, using intact antecedent packets only. The six new equalities yield target-lane possibilities of **(1, 0, 1, 4)**: no new lane-1 word. Combine them with the independently reproduced 25 intra-packet witness possibilities **(4, 5, 6, 8)**. After deduplication, this yields **5 × 5 × 7 × 12 = 2,100 complete four-word packets**, versus the predecessor's 960. Temper, serialize in the actual little-forward view, XOR the unchanged original K04 route mask, SHA-256 each full 16-byte candidate and compare the complete original slot commitment.

**Result: 0/2,100 authentic K04 hits.** The exact native MT19937 seeded positive control reconstructs a four-word successor from a five-word predecessor and a four-word lagged packet, including the packet-boundary pair. The full implementation is the [source-pinned single-file reproducer](../agents/agent8/k04_mt_packet_boundary_sft.py).

## Stage consistency prevents promoting individual predicted words

A second calculation expresses the original 25 intra-packet witnesses as equalities on cumulative native word stages S, then adds each new boundary witness. For the new boundary witness (r,k,l,i,q), the necessary equalities are:

- S[k] - S[r] = 400 - i
- S[l] - S[r] = 627 - q
- S[r+1] - S[r] = 4 (no interpacket hidden word)

Use integer source-row consumptions 4..100 for ACK packets and 0..100 for REQUESTED packets, with the original selected row's bytes withheld. The prior 25-witness base system is feasible. Individually, new witnesses **(33,86,116)**, **(40,94,125)** and **(43,97,130)** are feasible, while the other **three** are infeasible even over the continuous relaxation. All six together are infeasible. If every source row is instead allowed zero-word consumption, the joint six-plus-25 system becomes feasible, showing the dependence on direct ACK-packet word consumption.

Moreover, transplanting **each of the six** new exact historical signatures to target row129 yields a stage-infeasible system **even before adding that new witness's historical equality** to the prior 25. Therefore none of the four additional target-lane predictions can be promoted as a source-consistent selected K04 byte under the tested single-global-MT producer.

The stage calculation was run locally with SciPy/HiGHS linear and integer feasibility; it is a conditional generator test, not a fact about the undocumented printer firmware. The source-pinned portable reproducer above independently covers raw witness discovery, real complete commitment checking and a seeded full-packet positive. It does not include the optional SciPy feasibility solver.

## Decision

This extends the source witness grammar to packet boundaries and actually tests all resulting whole K04 components. **It does not solve K04.** The cross-boundary equalities alone are real arithmetic relations, but their global-stage implications conflict with a direct four-word ACK stream and cannot transfer coherently to the selected row. Do not expand the same boundary candidates or confuse an exact isolated relation with actual coupon provenance. A genuinely different printer producer, physical media or explicitly source-defined stage rule remains necessary. Original six PASS slots remain untouched; K08 is unresolved; combined REC8/1 remains INCOMPLETE.
