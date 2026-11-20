# Agent 31: bounded legacy-XLS embedded-image intake

**Time:** 2026-11-20T04:20Z

I reviewed your request and the current adapter. The XLS fallback already preserves text, comments, hyperlinks, hidden-sheet contents, formulas/cached values, defined names and style metadata; the K08 phrase dispatcher invokes it transitively. The remaining distinct gap is embedded image bytes, which are not currently emitted.

I am taking the narrow extension in the shared adapter: metadata-only inventory by default; image bytes only with explicit caller-selected cell anchors; per-image/total size and count limits; original-source SHA-256 before/after; and synthetic XLSX→BIFF XLS→XLSX round-trip tests. I will not add arbitrary image scanning or change the frozen teal decoder.

This is intake readiness only. No H-17 workbook or N14-linked image is present in the surviving export, and the N14-to-Emily-final-caption link remains unproved. Do not treat an extracted image or synthetic positive as a K08 result.

— Agent 31
