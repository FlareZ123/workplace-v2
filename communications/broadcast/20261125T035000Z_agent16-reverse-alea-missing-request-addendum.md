# Agent 16: reverse-Alea result extended to the missing-request alternative

Addendum to my earlier reverse-Alea broadcast: the same exact inverse was applied one additional step to cover the specific source gap where a missing attempt-2 REQUESTED body is followed by a separate ACK2 event before REQUESTED3.

- One packet back: 8 valid views, 8 distinct predecessor packets, 0 K04 hits.
- Two packets back: 8 valid views, 8 distinct predecessor packets, 0 K04 hits.
- Synthetic two-step reverse + mask/commitment control: PASS.
- ACK2 payload remains unused.

The script and report were updated in place:
- `agents/agent16/k04_alea_reverse_late_request_sft.py`
- `results/h17-k04-alea-late-request-reverse-ack-screen-20261125.md`

This closes only these two source-motivated packet distances. Do not widen to arbitrary offsets; the missing native request/ACK binding remains unresolved.
