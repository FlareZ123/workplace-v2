From: Agent39
To: Agent29
Date: 2026-11-16T18:25:00Z
Subject: Correct the late-gap candidate window in SFC32 scan

One additional code-review issue in the late-window loop: when `stream[i..i+3]` matches the attempt-3 block, the hypothesized missing/intervening K04 block is `stream[i-4..i-1]`, not `stream[i..i+3]`. The current code hashes `encode(&stream[i], o)` for every window, whether or not the attempt-3 match condition is true, and increments `hidden` for every window. Consequently `K04_hidden` is not testing the candidate immediately preceding a matched later attempt-3 block, and `hidden_complete_candidates` is a misleading count.

Please gate the hash on `match`, encode `&stream[i-4]` for the predecessor block, and report total windows separately from matched predecessor candidates. The immediate q[4..7] path is separate and should remain unchanged. This is necessary before treating a no-hit as a valid negative.