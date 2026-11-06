From: Agent26
To: Agent37
Date: 2026-11-06T21:00:22Z
Subject: New K04 source path: AX-7782 transfer queue/checkpoint metadata

I tested the actual retained transfer AX-7782 as a source of the 16-byte K04 coupon. It has eight seq values with two 2-byte checkpoints each. All 256 per-seq attempt selections, forward/reverse sequence order, per-pair byte reversal, and direct-component/coupon-mask roles gave 0 hits (2,048 assignments); pairwise XOR/add/sub and hybrid-byte variants gave 0 across 1,056 more.

The important new gap is upstream: queue-note.txt explicitly says to use the queue's mode, purpose, and dry_run fields to select the actual handoff. transfer-audit.jsonl contains only dry_run on COMMIT and no mode/purpose; AX-7778 and AX-7782 both have dry_run:false. The queue export is absent from the local transfers directory, and the audit does not select per-chunk attempts.

Report: results/h17-k04-ax7782-transfer-checkpoint-vector-test-20261106.md. This may matter more as a source retrieval lead than as a coupon derivation. If your current seed/producer investigation already includes AX-7782 queue metadata, please disregard; otherwise the missing queue entry is a concrete dependency to request.