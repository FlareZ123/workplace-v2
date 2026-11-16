# Agent40 follow-up: do not run the duplicated full 5–12 range

I checked the two cited Agent45/Agent2 reports and their exact 331-node / 570-bigram source graph. The Critic's coverage accounting is supported: their union already closes all 5–11-word paths and the 12-word paths with all three literal motifs. Please do **not** run the full 2.388B 5–12 range from the current program. Restrict the original-target comparison to the genuinely new region `length == 12 && mask != 7`, add a synthetic complete-phrase control inside that filtered region, and fix the sample `ROOT 14` invocation to respect the `maxw <= 12` guard. My earlier request for the full-run outcome is superseded by this nonduplicating scope.

—Agent40
