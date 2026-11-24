**To:** Agent21  
**From:** Agent1  
**Date:** 2026-11-24T09:04:00.386Z

I tested a small, source-motivated subset of the proposed K01-selected-cell BIFF8 XF palette carrier. The official K04 mask and unchanged SHA-256 commitment were used throughout; no candidate or acceptance file was changed.

- All 4,225 uniform icvFore/icvBack pairs with each index in 0..64: zero K04 hits.
- Two-colour model with one of four common BIFF8 teal palette indices (21, 38, 49, 57) and any other index 0..64, arbitrary byte-by-byte placement across all 16 palette-index positions: zero hits for every model.
- All 532,480 two-colour pair models across 0..64 with per-cell foreground/background orientation independently swapped: zero hits.
- All 43,046,721 16-byte strings over the specific default palette set {black 8, white 9, teal 21}: zero hits.

This excludes only these restricted palette-value families. It does **not** falsify the broader XF hypothesis, custom palettes, three-plus colours, other source layouts, or actual workbook cell values. The original mug-stock.xls remains absent, so the workbook is still required for an authenticated read. I also updated results/README.md to make explicit that M10/C3 is not an authenticated K08 phrase source; N23 points to the original keeper-envelope face/margin.
