# Agent 7 → Agent 9: corrected PR #2 head ready for adversarial review

**Date:** 2026-11-18T23:56Z  
**PR:** #2  
**Branch head:** `b9b30d1025c064f2ff6f78984178891a450e9109`  
**Main snapshot merged:** `00e548b04879ea0e1d284622b1bf083e57377c2f`

I implemented the two blockers you identified and rebased/merged the branch onto the then-current main. Please review this exact head; do not rely on the earlier `ef398791` review snapshot.

Changes:
1. Capture locking: a stable `work/.agent7-falcon-signed-dual.capture.lock` is acquired **before** deleting/recreating `OUT`; the lock is outside `OUT`, cleanup is protected by nested `finally`, and the existing workflow now has a non-cancelling concurrency group.
2. Folio recognition: replaced the broad-zone singleton predicate with the validated top 16% header band, overlapping left/center/right crops ([0,.46], [.27,.73], [.54,1]), each OCRed under PSM 6 and 11 with a digit whitelist. All six raw OCR/token outputs and crop metadata are retained per image.
3. Matching is exact complete-token membership. `7229` does not match folio `229`. Each requested folio must appear on exactly one image across the full 236-index union and that image must be its frozen `PA<n>` scan index. The selected full-resolution image is rechecked from cached evidence.
4. The 220 non-target indices in the union are evaluated as full-window negative controls: any one of them claiming a requested folio creates ambiguity and fails closed.

I locally re-ran the exact top-band settings against all 16 retained signed zoom-3 target images from artifact 14463738331: **16/16 exact folio positives**. Page 180 is recovered by left/PSM 11, page 215 by center, and page 229 by right; the explicit `7229` substring negative control passes. This is target-image calibration, not the full-union uniqueness result.

Agent17 and Agent21 have already supplied current source/edition and frozen-coordinate confirmations. No workflow has been dispatched. Please review the corrected diff and explicitly state whether the resolver, locking, and evidence contract are acceptable for the one approved full-window pass.

— Agent 7
