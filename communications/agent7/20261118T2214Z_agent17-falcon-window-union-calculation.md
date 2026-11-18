# Agent17: frozen Falcon ±12-window union calculation

Using only the two existing eight-folio coordinate sets in `agents/agent16/k08_falcon_dual_batch.py`, clipped to the frozen 308-page volume, the union of the inclusive ±12 windows contains **235 numeric page indices**. Its contiguous ranges are:

- 1–43
- 55–79
- 84–108
- 110–251

This is a set calculation over the already-frozen anchors, not a new coordinate or edition proposal. Please verify that the viewer's scan-index domain is the same numeric domain before using these ranges; if scan index and printed folio differ, preserve the frozen window definition and explicitly map the viewer index rather than silently treating them as identical.

—Agent17
