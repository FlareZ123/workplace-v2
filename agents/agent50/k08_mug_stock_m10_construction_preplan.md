# K08 mug-stock workbook: pre-registered cell-construction test

**Owner:** Agent 50  
**State:** hypothesis / not yet testable from the supplied export  
**Created:** 2026-11-20T01:58Z

## Question

Can the final Emily recovery-envelope caption be emitted as a complete text value from the legacy `mug-stock.xls` workbook, using the surviving source's coordinate and wrap-text cues, rather than by inventing phrase fragments?

## Fixed source observations

- The retired-office bookmark #3 names `R:/Stores/consumables/mug-stock.xls` as “Tea-room stock sheets”.
- The signed K01 component consists of four ordered ink groups A/B/C/D. Reading each adjacent byte pair as (row byte, column byte) gives `EX4, AT171, HN28, DZ122, DT205, AI96, C67, Z201`, grouped two per K01 group.
- The official K05 low-bit output is `03 43` = C3. The source-derived LOW-IF-EVEN alternate K05 stratum gives `0A 4D` = M10; a separate note/seal path also gives M10. This alternate stratum is not the official K05 component.
- The C3→MAIL03→MAIL09→MAIL13→MAIL04→MAIL10 route has subject initials WRAPT. “Wrap text” is a hypothesis, not an explicit source instruction.
- The local export contains no workbook. The 8 MiB AX-7782/Bundle06 object is not present; only 2-byte transfer checkpoints survive.

## Frozen candidate model

If an independently authorized native `mug-stock.xls` is supplied:

1. Preserve the original bytes and SHA-256; do not open/save the original in spreadsheet software.
2. Identify workbook sheets and visibility, dimensions, formulas/cached values, comments, hyperlinks, defined names, cell styles, and hidden rows/columns using the existing read-only BIFF adapter.
3. **Primary candidate:** the complete stored/displayed text value of cell `M10` on a uniquely identifiable relevant stock sheet. The only permitted representations are the cell's literal text value and, if formula-backed, its cached displayed value; keep them separate. Apply the unchanged K08 normalization and HMAC to each complete value. Require a unique exact acceptance hit. Do not concatenate fragments or try neighboring cells if M10 fails.
4. **Cell-style discriminator:** record whether M10 has `wrap_text=True`; this is a pre-registered support/control for the WRAPT cue, not a requirement to mutate the text. Record fill/font colors and number format. Absence of wrap-text or a text value weakens/falsifies this specific M10 model.
5. **Source-coordinate controls:** inspect only C3 and the eight K01-derived cells, in source order and group order:
   - A: EX4, AT171
   - B: HN28, DZ122
   - C: DT205, AI96
   - D: C67, Z201
   Preserve exact sheet names; do not invent A–D sheet assignments. If there are uniquely labelled A/B/C/D sheets, report the corresponding group cells separately.
6. For the eight K01 cells, if and only if all eight are numeric, test the already pre-registered low-bit sequence `1,0,1,1,0,0,1,0` (first bit as LSB = `0x4D`). Do not change bit plane, order, or orientation after observing the workbook.
7. C3 is a locator/control, not a phrase candidate. P212 remains conditional and is not used as the primary cell because its AX-7782 derivation uses mixed retry attempts that conflict with the accepted K07 rule.

## Stop conditions

- If the workbook is absent, no candidate is generated.
- If M10 is not a complete text value on a uniquely identifiable relevant sheet, this model fails; do not pivot to all cells, arbitrary comments, broad phrase scans, or other coordinate permutations.
- A style/coordinate match without an exact K08 HMAC is not a recovery.
- An exact HMAC/acceptance hit is candidate evidence; preserve workbook provenance and independently verify the original source relationship before calling it historically authenticated.

## Tooling

Agent 9's `work/h17_xls_lo_fallback.py` is the current read-only BIFF adapter and is integrated with `work/h17_ax7782_k08_phrase_intake.py`. The adapter currently emits values, comments, hyperlinks, formulas/cached values and defined names, but as of this preplan it does not emit cell style/alignment metadata. Agent 50 requested a bounded style extension from Agent 9 at `communications/agent9/20261120T015600Z_agent50-biff-style-metadata-gap.md`. Do not create a duplicate scanner while that coordination is pending.

## Current conclusion

The surviving sources locate a plausible workbook carrier and a small, falsifiable cell test. They do not supply the workbook, do not specify a complete caption extraction rule beyond this testable hypothesis, and do not reveal any K08 words. Keep K08 unresolved until an authorized workbook or direct final-caption witness is available.
