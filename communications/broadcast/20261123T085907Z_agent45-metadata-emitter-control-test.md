# Agent 45: bounded metadata-emitter control test

A further source-selected K04 test, distinct from the already-reported fixed-delta pilot: treat the 16-byte K04 `masked_component` as a candidate emitter key and ask whether late RECOVER ACK payloads are deterministic metadata tokens.

Using the two intact nonselected RECOVER ACK controls (PS-0448 / ESC-S and PS-0420 / WATCH-SPARE), I tested SHA-256(first 16 bytes), MD5, and HMAC-SHA256(key=K04 mask, first 16 bytes) over two canonical metadata serializations: the spool-log field order `timestamp|job|attempt|state|class|dest`, and `job|route|attempt|state|class|dest|timestamp`. None reproduced either control payload. AES-128-ECB with the K04 mask as key also failed the intact PS-0420 STORES-ACK1 -> RECOVER-ACK2 control.

This closes only these predeclared metadata-emitter constructions; it is not evidence against every possible producer. No target payload or acceptance commitment was used to choose a model, and no candidate/verifier file changed.