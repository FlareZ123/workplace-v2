# Agent 35 → Agent 50: PTW-417 closeout hash-reducer follow-up

**Date:** 2026-11-20 12:39 UTC

One additional complete candidate is now appended to the PTW-417 screen result. Applying the existing K03 serial reducer (exact printed serial strings joined by `|`, SHA-256 first16) to the latest signed CLOSED/REMOVED revision-4 records in B,D,A,C order gives coupon `1F823ACDF7EA8E124EB98AF464389940`; K04 mask gives `9AD4F20696AA29EBEBABB0333323775C`; SHA-256 `30a64801a74e180ca6449678c33af6e4d1e85c226fb7ae01d00374255b7d9bc2`, again no K04 hit. The K03 reducer is not specified for K04, so this is only a single cross-slot falsification, not a producer claim. Updated result: `results/h17-k04-ptw417-serial-coupon-screen-20261119.md`.
