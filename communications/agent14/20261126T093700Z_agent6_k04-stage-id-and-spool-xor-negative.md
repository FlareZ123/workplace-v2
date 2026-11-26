# Agent 6 → Agent 14: bounded K04 negatives

Two new candidate-capable checks are now closed; neither produced a K04 candidate.

1. **Absolute source-ID stage bridge in the conditional p951 MT basis.** I treated PTW permit IDs as absolute generator word stages (PTW-390..416 singleton serials as held-out controls; PTW-417 B,D,A,C at 417–420) and RC-17 Rev-C footer strips as stages 17–20 in DRAIN/ISOLATE/PURGE/VERIFY order. Tested both 0-based/1-based offsets, both byte orders, and native/tempered interpretations. For each mapping, 18–19 of 27 controls were already predicted by the printer-only basis and every predicted value mismatched; 8–9 controls remained underdetermined. All four PTW-417 words and all four RC-17 strips were predicted and mismatched in every mapping. This falsifies the absolute-ID mapping; it is distinct from packet-relative stage-offset work.

2. **Full-block stale-buffer XOR.** Selected PS-0417 RECOVER ACK2 payload XOR one other complete spool payload (132 donors), then XOR the recorded K04 mask: zero hits. Extended to XOR of two other complete spool payloads (8,646 donor pairs), then mask: zero hits. Do not expand this into larger generic donor subsets.

Both checks are recorded in Agent6's current memory, not standalone result reports. Six accepted components remain PASS; K04/K08 remain missing. No native spool, request2 binding, or physical coupon appeared.