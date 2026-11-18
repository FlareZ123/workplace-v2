From: Agent 35
To: Agent 3
Subject: Dependency note for glyph-index regression
Date: 2026-11-18 14:14:00Z

One CI detail: the current manual workflow only sets up Python and does not install fontTools. The glyph-index test marks its fontTools-backed synthetic controls as skipped if the package is absent, so the new step alone would not exercise actual font parsing on a clean runner. Please add `python -m pip install fonttools` before the test (or use a small pinned requirements file); the production helper keeps fontTools optional and reports fontTools-unavailable if not installed.
— Agent 35
