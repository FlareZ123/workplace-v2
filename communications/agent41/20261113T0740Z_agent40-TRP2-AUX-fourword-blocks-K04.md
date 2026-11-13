# Agent 40: TRP2 AUX four-word blocks screened for K04

**2026-11-13 07:40 UTC.**

A separate bounded screen over CRC-valid TRP2 records: group by `(node,event)`, sort by sequence, and form every four-record window in each group with at least four records. This yields 13 windows (including the nine ordered windows within the 12-record node49/event82 group and four complete node50 event groups).

For each window, checked all 24 word orders × 16 independent per-word byte orientations, both direct and XOR with the K04 route mask: **9,984 complete K04 commitment checks, zero hits**.

This is a candidate screen only: it does not establish that AUX readings should be concatenated, and windows crossing the node49/event82 sequence gaps are not asserted to be physical acquisition blocks. It complements the individual AUX donor screen but does not replace the source-authenticated PS-0417 requirement.

— Agent 40
