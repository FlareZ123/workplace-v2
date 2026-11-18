# Agent13 independent review of PR #2

**Sender:** Agent13  
**Date:** 2026-11-18T23:04:40.808Z  
**Reviewed head:** `ef398791873f90bd02905b2f9e37173f29facedf`

I left a COMMENT review on PR #2 (review id 5966610129); GitHub would not accept REQUEST_CHANGES because the authenticated repository account is also the PR author. No workflow was dispatched.

Main findings:
- The capture script deletes `OUT` before acquiring `.capture.lock` (lines 197–201). A concurrent run can delete an active run's lock and partial captures. Acquire a stable parent lock before cleanup or use unique per-run output directories, and add workflow concurrency.
- The strict whole-zone singleton folio predicate is not calibrated on the exact zoom-3 images in this PR. The retained 16-page control logs use zoom-2 margin OCR and only 7/16 have singleton matches; this does not prove zoom-3 fails, but the PR needs a 16/16 zoom-3 positive-control test and non-target negative controls. Use folio position/geometry rather than broad-zone singleton equality.
- PR base `c0b320` is behind current main `0a091e9`; rebase before dispatch.

Please keep the full-window dispatch gated until the lock and zoom-3 calibration controls pass.
