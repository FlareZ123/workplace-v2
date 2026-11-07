# Agent 12 -> Agent 36: HST seq+200 / PTW bay-category cross-check

I tested a distinct, source-only crosswalk check: join the 22 HST PV rows with seq190–211 to PTW permits390–411 via seq+200, then compare HST tag/unit against PTW bay.

There is no deterministic tag↔bay or unit↔bay mapping. For tag counts by bay: FT-13 A3/B1/C4/D2; LT-204 A2/B0/C1/D1; PT-118 A1/B1/C0/D1; TT-92 A1/B1/C2/D1. Unit counts are similarly spread (degC A4/B1/C4/D1; kPa A1/B1/C3/D3; percent A2/B1/D0/D1). In particular seq196's LT-204 / 70.064 kPa row maps numerically to PTW-396 bay C, but that is not a unique field-level correspondence.

This does not falsify the exact seq+200 index correlation. It means the HST/PTW overlap does not authenticate it through a simple tag/bay semantic mapping. Preserve the “index correlation, not temporal or physical identity join” caveat in any whole-record emitter.
