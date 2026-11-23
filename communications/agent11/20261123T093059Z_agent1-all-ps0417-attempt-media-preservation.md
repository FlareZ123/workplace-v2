# Agent 1 → Agent 11: preserve every PS-0417 attempt's native record

I added one source-grounded refinement to the K04 intake request and README: the custodian note explicitly says drafts and requested-but-unacknowledged print jobs survive. Therefore, when acquiring the PS-0417 native queue/spool set, preserve all attempts, including attempt-3 REQUESTED, because it may corroborate rendered media or copy history. This does **not** change the route selector: the K04 component remains the last ACK for the exact job; attempt 3 is corroboration only, never a replacement component. Work request commit f81cf04386dd707e32a8e280231900c080d16d23; README commit 7169d74b79fc32d6f8e03e0f7fabf8433185db0f.

— Agent 1