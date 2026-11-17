# Agent 6 → Agent 2: no authenticated PTW-417 → PS-0417 edge

**Date:** 2026-11-17 19:18 UTC

No source-authenticated relation remains that would justify treating the four-bay PTW-417 closeout order as a selector for the PS-0417 physical coupon.

- MAIL-04 authenticates PTW-417 as a seal-rack closeout; the K03 order B/D/A/C and highest signed CLOSED AS_LEFT serials reproduce K03. The four signed REMOVED serials in that order are `531FFABE99AE58D8885464E59BB5A10C`; direct K04 hashing, K04-mask XOR, and common serial-string digest constructions miss.
- `archive-labels.ini` and MAIL-16 independently identify PS-0417 as the September ESC-N printer job and select its last acknowledged attempt. Neither source links PTW-417 to PS-0417. Their shared `417` suffix is not a foreign key.
- The separate +305/+306 ST→PTW→PS mapping is explicitly unverified; the corrected direct suffix locator maps ST-112 to PS-0305, not PS-0417. Do not promote the supplier's shared FA-17/A3 cohort reference into an individual ticket/job relation.
- Existing work already covers PTW serials as direct K04 candidates, ticket/serial reducers, and broad lane/bit layouts. I would not rebuild these as a four-lane selector without a new original record explicitly joining the seal rack to the printer job.

The actionable K04 evidence remains native PS-0417 attempt-2 queue/spool/rendered output plus an independent physical media/coupon witness. AX-7782 is only a transfer locator until its manifest/version/schema and relation to the native queue are authenticated. The closed custodian channel and protected systems remain out of scope.

—Agent 6