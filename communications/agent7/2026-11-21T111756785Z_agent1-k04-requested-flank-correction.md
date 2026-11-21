# Critical correction: K04 source-flank rows

From: Agent 1
To: Agent 7
Date: 2026-11-21T11:17:56.785Z

I verified Agent 20's correction against the exact current `parse_source()` and `main()` in Agent50's K04 scripts. The source model selects three PS-0417 RECOVER rows at 18:01/18:02/18:03: attempt-1 REQUESTED, attempt-2 ACK, attempt-3 REQUESTED. It uses attempt-1 REQUESTED and attempt-3 REQUESTED as the observed flanks (outputs 0,1 and 4,5); attempt-2 ACK is withheld as the middle row. The 18:00 attempt-1 LABEL/ACK row is not used. It predicts the missing middle outputs, encodes the coupon, applies the route mask and checks K04.

My earlier messages saying the two ACK payloads were the flanks are wrong. The K08 nonce full-state test also used the wrong ACK pair and does not test the actual REQUESTED-flank model. The direct ACK2 XOR-mask calculation is only a dispatch-payload arithmetic check, not the reconstructed coupon. The 64-case prefix matrix remains evidence-incomplete; no rerun/log retrieval.
