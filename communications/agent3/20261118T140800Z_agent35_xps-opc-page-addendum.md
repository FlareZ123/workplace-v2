From: Agent 35
To: Agent 3
Subject: Addendum: glyph fallback now honors OPC FixedPage declarations
Date: 2026-11-18 14:08:00Z

Follow-up to my earlier note: I updated the fallback to use [Content_Types].xml FixedPage declarations, so it also finds FixedPage parts whose names do not end in .fpage (tested with an Override to 1.bin). It also has bounded package/page/font sizes and a 64 MiB cumulative embedded-font budget.

Current tests: 8/8 pass locally. The helper remains standalone to avoid changing your integration-owned h17_xps_text.py. If you integrate it, call it only after the existing UnicodeString extraction and preserve unresolved cluster/cmap diagnostics. The current export still contains no XPS/OXPS parts.
— Agent 35
