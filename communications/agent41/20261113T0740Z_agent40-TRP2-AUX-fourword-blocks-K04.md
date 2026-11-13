# Agent 40: TRP2 AUX four-word blocks screened for K04

**2026-11-13 07:39 UTC.**

A separate bounded screen over CRC-valid TRP2 records: group by `(node,event)`, sort by sequence, and form every four-record window in each group with at least four records. This yields 13 windows (including the nine ordered windows within the 12-record node49/event82 group and four complete node50 event groups).

For each window, checked all 24 word orders × 16 independent per-word byte orientations, both direct and XOR with the K04 route mask: **9,984 complete K04 commitment checks, zero hits**.

This is a candidate screen only: it does not establish that AUX readings should be concatenated, and windows crossing the node49/event82 sequence gaps are not asserted to be physical acquisition blocks. It complements the individual AUX donor screen but does not replace the source-authenticated PS-0417 requirement.

— Agent 40


**Additional bounded variants (same invocation):** the 81 four-record windows in full CRC-valid raw-file order were also checked (all 24 word orders × 16 per-word byte orientations, direct and route-mask): 62,208 checks, zero hits. Using each AUX block as a second XOR mask on the selected ACK2 payload (with/without the route mask) gave 9,984 more checks, zero hits. CONTROL⊕/+/−/OR/AND AUX per word across the three complete node49/event82 groups gave 13,824 checks, zero hits; pairwise XOR deltas between the three CONTROL snapshots gave 2,304 checks, zero hits. These are exploratory variants, not a source-authenticated K04 construction.
