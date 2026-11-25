# Agent 16: bounded reverse-Alea test of late PS-0417 REQUESTED3

I tested a distinct direction from the earlier forward Alea screen. The earlier work found 8/384 valid Alea/MWC3 serializer views of the late attempt-3 REQUESTED payload. This screen inverted the exact lag-3 multiply-with-carry recurrence from each of those views to reconstruct the immediately preceding four-word packet, then applied the routed K04 mask and full commitment check.

- 384 serializer views; 8 satisfy the carry condition and exact forward replay.
- 8 distinct preceding 16-byte packets recovered.
- **0 K04 commitment hits.**
- Deterministic synthetic reverse + mask/commitment positive control passed.
- The selected attempt-2 ACK payload was not decoded or used.

Script: `agents/agent16/k04_alea_reverse_late_request_sft.py`  
Result: `results/h17-k04-alea-late-request-reverse-ack-screen-20261125.md`

This closes only the conditional one-packet reverse-Alea hypothesis. MAIL-16 identifies attempt 3 as a button press with no ACK; the export does not authenticate its payload as printer output or establish that it is adjacent to ACK2 in one uninterrupted generator stream. Do not expand this into further Alea seed/phase/serializer sweeps. K04 still requires a source-authenticated native PS-0417 queue/job image or request/ACK binding.
