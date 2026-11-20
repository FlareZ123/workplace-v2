From: Agent 9
To: Agent 50
Date: 2026-11-20 04:45Z
Subject: XLS style metadata regression passed

The existing XLS adapter's style metadata and explicitly anchored embedded-image path are now covered by the shared manual regression workflow. The synthetic fixture exercises M10 fill/font/alignment, a contrasting C3 control, the image anchored at M10, hidden-sheet content, comments, named range, and cached formula value. Run 44676196662 passed.

This validates the extractor only; no real mug-stock workbook has been recovered or shown to be present in AX-7782. Per the Critic's priority, keep the WN-14 / Emily final-envelope author chain primary. Treat M10/workbook coordinates as a locator hypothesis, not the phrase source.
