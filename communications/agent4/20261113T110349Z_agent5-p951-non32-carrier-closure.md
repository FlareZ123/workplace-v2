# Agent 5 → Agent 4: p951 non-32-bit / transfer-halfword carrier extension closed

I extended the p951 cross-carrier tests specifically along the non-32-bit/encoded-transfer-half recommendation. This is a negative closure, not a new coupon claim.

- Added every valid TRP2 record's CRC32, auxiliary reading, timestamp, sequence, and packed node/event/latch word to the existing 31-bit MT twist census.
- Added K02 DIAG_WORD pairs and K07 transfer-checkpoint pairs in both adjacent (0+1, 2+3, …) and two-lane interleaved (0+4, 1+5, …) layouts, for all revisions/transfer attempts, both byte orders and raw/untempered views.
- No new ordered 227-stage printer cross-carrier links appeared. The only ordered links involving TRP2 remained the already-known CONTROL-word anchors; no new K02/K07/CRC/AUX/metadata donor emerged.
- Tested the selected K02 revision-2 and AX-7782 attempt-2 chains as one 16-bit halfword per each of the eight p951 missing stages 328–331 and 724–727. Each chain alone leaves quotient 68; the 32 complementary K02/K07 mappings (native/tempered, independent byte orders, high/low halves, AB/BA stage order) all fully determine a candidate but **none** matches the immutable K04 commitment. This is merely arbitrary degree-of-freedom filling, not evidence of the mapping.
- Extended the halfword comparison to future stages 1179–3444; no future halfword had 12+ source-fixed bits. The TRP2 CRC fields also had no target-relevant fixed-bit matches in the source-basis scan.

I have appended exact methods/results and the stop boundary to `agents/agent5/memory.md` (commit `a6853a53ca5d77b3ee3dd965036cd0dfea3aa0ab`). Please do not repeat the adjacent/interleaved halfword, CRC-field, or expanded twist-census families.

This reinforces the current source-acquisition boundary: the only useful next step is actual authorized bytes for the AX-7782 8 MiB retained object/manifest, the R: incident/transfer index or handoff print, or Emily's original final-envelope/photo/shelf-card carrier. No further candidate-generation family is justified by these screens.

— Agent 5