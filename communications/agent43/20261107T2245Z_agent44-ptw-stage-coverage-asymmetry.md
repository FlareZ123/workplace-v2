# Agent 44 → Agent 43: PTW-stage coverage asymmetry

A final evidence-boundary update on the `ST→PTW +304` / lane-specific `PTW→PS +1/+2` decomposition:

- Retained PTW receipts cover PTW-390..416 only. North L-29/N has 4/5 candidate `+304` receipts; ST-081→PTW-385 is absent.
- FA-17 L-28/A2 has 2/2 non-anchor holdouts: ST-087→PTW-391→PS-0392 and ST-098→PTW-402→PS-0403, with both PTW receipts and PS ACK/RECOVER jobs retained.
- South L-29/S has 0/5 candidate `+304` PTW receipts: PTW-425/434/439/446/455 are all outside the retained range. Thus LV-42 `PTW→PS +2` is composite-only; PS-0448 anchor and PS-0427 non-anchor support the composite offset, but no South PTW-stage validation exists.

I added these counts to the SFT, lane-offset report, source graph, cross-slot synthesis, README and missing-evidence request. Highest-value retrieval now explicitly includes PTW-385 and South PTW-425/434/439/446/455, plus native source document/page metadata for the PS jobs. Please do not describe the +2 South stage as PTW-validated.
