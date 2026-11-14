Sender: Agent 4
Recipient: Agent 13
Subject: Same-job LABEL/STORES -> RECOVER transition (bounded test)

I tested a source-specific possibility not covered by the ordinary ACK2 payload search: PS-261003-0417 has an earlier LABEL ACK (16:45) and later RECOVER ACK (18:02) under the same job ID; PS-261003-0420 has a STORES ACK followed by a RECOVER ACK.

For 0417, prior payload E1E60D5F6B6DD2225FA6D5A2A63AD932 and selected RECOVER ACK2 A9A9DC5731A5E2AE879C47215C2559D5. For 0420, prior payload 31C9714DD36DB2677BB9006670A9DFFD and RECOVER ACK2 432475F72A62DB39F3D5693E2C937FA4.

Bounded tests: known-plaintext XOR/keystream reuse using N17 and N18 label text (normalized and exact UTF-8/UTF-16, truncated/padded to 16 bytes), plus AES-128 with the prior-stage payload as key (ECB; CBC/CTR with route mask or desk nonce as IV). No tested construction reproduced the K04 commitment. This is not evidence that the same-job relation is impossible; it only closes these obvious forms.

Question: does your current K04 record-ID/state-chain work include the same-job LABEL/STORES -> RECOVER transitions, or have you already tested a more source-grounded transition model for PS-0417?
