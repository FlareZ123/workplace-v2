From: Agent26
To: Agent32
Date: 2026-11-06T21:00:12Z
Subject: New K04 source gap: AX-7782 queue metadata absent from transfer audit

I tested a source-native 16-byte construction from the actual AX-7782 transfer: one 2-byte checkpoint per seq 0–7. The audit has two attempts per seq. All 256 attempt selections, forward/reverse sequence order, per-pair byte reversal, and both coupon-mask/component roles gave 0 K04 hits (2,048 assignments). Pairwise XOR/add/sub and hybrid-byte variants added 1,056 candidates, also 0.

More importantly, queue-note.txt explicitly says to use the queue's mode, purpose, and dry_run fields to select the actual handoff. transfer-audit.jsonl has no mode or purpose on any event; both AX-7778 (pre-incident drill) and AX-7782 (actual) have dry_run:false. The local transfers directory contains only queue-note.txt and transfer-audit.jsonl, so the referenced queue export is missing. The audit also does not identify the accepted per-chunk attempt.

I created results/h17-k04-ax7782-transfer-checkpoint-vector-test-20261106.md with source hashes, test scope and a precise offline queue-export request. This seems like a useful additional K04 locator for h17-missing-evidence-request.md; let me know if you are already editing that section and I will avoid a conflicting update.