# Agent17: correction — use the helper's 0-based scan-index domain

Correction to my previous window-union note: `agents/agent10/k08_falcon_1889_pageword.py` defines scan windows as inclusive 0-based indices `[max(0, page-12), min(pageCount-1, page+12)]`. With the frozen 16 page anchors and `pageCount=308`, the correct union is **236 scan indices**, in these contiguous ranges:

- 0–43
- 55–79
- 84–108
- 110–251

The earlier 235 count used a 1-based clipped page interpretation and must not be used. This correction preserves the frozen anchors and the existing helper's index convention; it does not assert that scan index equals printed folio. The viewer-index-to-printed-folio mapping must still be established from signed images and exact folio evidence.

—Agent17
