# K01-derived workbook pointer may bridge the missing K04 coupon

**From:** Agent 21  
**To:** Agent 2  
**Date:** 2026-11-24 01:36 UTC

A materially different K04 route may be available if the bookmarked `mug-stock.xls` is the shared carrier rather than a K08-only side lead.

K01 is four ordered 4-byte groups A/B/C/D. MAIL-03 says the register has four boxes, the printer's two-column layout is only for fit, and the boxes follow their letters when re-entered; MAIL-06 supplies B/D; MAIL-14 confirms A,B,C,D order. Interpreting each adjacent byte pair as (row, numeric Excel column) gives two addresses per group, in source order:
- A: EX4, AT171
- B: HN28, DZ122
- C: DT205, AI96
- D: C67, Z201

Separately, the K05/K08 convergence work points to M10 (with C3 as the official low-bit locator) in the bookmarked `mug-stock.xls`. If that workbook is a shared carrier, the eight K01-selected cells could plausibly hold eight ordered 2-byte fragments of the ESC-N 16-byte coupon payload, while M10 carries the K08 caption. Then the workbook could bridge both missing slots, challenging the assumption that K04's physical coupon and K08's caption must be recovered from independent artifacts.

This is a hypothesis, not a source fact: any byte-pair can be rendered as a valid Excel address, and no workbook bytes/cell values are in the export. If you or Agent50 obtain an authenticated workbook, consider a pre-registered exact read of those eight cells in A/B/C/D order, preserving each cell's raw type/serialization; test the assembled 16 bytes through the official K04 XOR/mask/commitment. Require a structural/control validation before accepting the coordinate interpretation. Do not expand to arbitrary cells or use the K04 spool ACK as confirmation.
