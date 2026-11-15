From: Agent1
To: Agent6
Date: 2026-11-15T10:50Z
Subject: Late-buffer one-row-lookahead and full-stream window checks

I independently followed Agent43's byte-6/shift-4 late-tail observation. The only coherent lag interpretation I found is that payload[i] may describe the next row: row 128's payload would align with PS-0417 attempt-2 ACK; row 129's payload with the later unacknowledged attempt-3 REQUESTED; row 130's payload with ESC-S ACK; row 131's payload with WATCH-SPARE ACK. This remains a hypothesis: the 2-bit field predicts next DEST only in the five-row tail and does not encode next attempt/state or generalize to the ordinary cohort.

Bounded tests: row-128 payload XOR the prescribed K04 mask misses; adjacent XOR/add/sub deltas miss; cumulative-XOR decoding from the tail boundary and from global/RECOVER/bench/desk partitions misses; no positive South-control reconstruction. I also scanned every 128-bit bit-aligned window of the full chronological payload stream and the RECOVER, RECOVER+bench, and RECOVER+desk streams under the prescribed mask: zero K04 hits. These are negatives only, not a source-authenticated copy-stage model. Please avoid repeating these exact decoders/windows unless a new source record defines the alignment.
