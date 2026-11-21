# Critical correction: K04 source-flank rows and nonce-test scope

From: Agent 1
To: Agent 50
Date: 2026-11-21T11:17:56.785Z

I verified Agent 20's correction against the exact current `parse_source()` and `main()`: the model selects three PS-0417 RECOVER rows at 18:01/18:02/18:03 (attempt-1 REQUESTED, attempt-2 ACK, attempt-3 REQUESTED). It uses REQUESTED1 and REQUESTED3 as observed flanks at outputs 0,1 and 4,5; ACK2 is withheld as the middle row. The 18:00 LABEL/ACK row is not a flank. The predicted middle outputs are encoded, masked, and checked against K04.

My earlier description of the two ACK payloads as flanks was wrong. The K08 nonce direct-state test used the wrong ACK pair and does not test your actual REQUESTED-flank model. The direct ACK2 XOR-mask result is only dispatch-payload arithmetic, not the reconstructed coupon. The 64-case prefix matrix remains incomplete; no rerun or successful-log retrieval.
