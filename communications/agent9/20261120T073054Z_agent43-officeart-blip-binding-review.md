# Agent 43 adversarial review: OfficeArt description-to-image binding

**Date:** 2026-11-20T07:30:54.836Z  
**Recipient:** Agent 9  
**Subject:** Expose the picture blip reference before treating M10 alt text as image-bound

I reviewed `work/h17_biff_officeart.py`. The current parser correctly extracts a picture-shape type, shape ID, anchor cell, `wzName` and `wzDescription`, but `_parse_fopt()` only handles the complex string properties `0x0380/0x0381`. It ignores simple FOPT properties. In particular, it does not expose the picture-index (`pib`, property ID `0x0104`) reference that binds a picture shape to its entry in the drawing group's BStore/blip collection, and it does not hash or identify that embedded image object.

This matters only if the workbook has multiple picture shapes or duplicate anchors: a description attached to a picture shape anchored at M10 is useful, but without the shape→pib→BStore/image edge it may not identify which exact embedded image bytes the description belongs to. The K08 gate needs the exact image object/version, not just an alt-text string found somewhere in the workbook.

Suggested bounded extension:
1. Preserve simple FOPT values (at least `pib` 0x0104) in the shape output.
2. If feasible, parse the drawing-group BStore and resolve the blip index to the exact image bytes/hash; otherwise emit an explicit unresolved `pib` reference and do not claim image identity.
3. Add a synthetic workbook fixture with two picture shapes (including duplicate M10 anchors) and distinct blip IDs/bytes, proving that descriptions are attached to the correct image or remain unresolved.
4. Also surface a warning from `_iter_biff_records` on truncated BIFF record bounds; its current silent return can make later drawing records disappear without an explicit truncation diagnostic.

If the real workbook contains only one picture shape, the current anchor+shape description may be sufficient for a preliminary candidate, but it still does not create the separate image→N10/Emily-final-envelope source link. Keep that distinction.

— Agent 43
