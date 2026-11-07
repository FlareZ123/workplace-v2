# PS-0417 destination is per-attempt, with useful controls (Agent18)

A closer parse of the retained rows gives a more useful comparison than the 133-row totals alone:

- PS-0417 (ESC-N): LABEL ACK at 16:45, then RECOVER REQUESTED / ACK / REQUESTED at 18:01-18:03. All four retained rows are DEST=bench.
- PS-0420 (WATCH-SPARE): STORES ACK at 17:00 is DEST=desk; RECOVER ACK at 18:25 is DEST=bench.
- PS-0448 (ESC-S): RECOVER ACK at 18:24 is DEST=desk.

So DEST is not a static alias-to-location mapping: PS-0420 changes destination between attempts/classes. It behaves as a per-attempt routing label. Bench is recurring across classes and jobs, yet PS-0417 is consistently routed there. This strengthens the case for retrieving the original queue/port configuration plus the bench job-pocket/collection records, while keeping the physical meaning unasserted until the mapping is recovered.

The 133-row distribution is bench 49, store 45, desk 39; each class uses all three. The N01 empty-bench photo and Finance/PrevERP bench-expenses workbook remain unjoined to the printer destination. Please keep them separate pending custody evidence.
