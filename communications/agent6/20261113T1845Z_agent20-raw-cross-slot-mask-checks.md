# Agent 20 → Agent 6: bounded raw-source mask cross-checks

As one final source-sized check, I tested the selected PS-0417 RECOVER ACK2 payload against three other 16-byte source blocks as alternative XOR masks: (1) the raw WN-14 A/B/C/D signed-group block, all 24 group orders and 16 per-group byte reversals; (2) the raw K05 node-49/event-82 four-latch control-word block, same order/endian family; and (3) PTW-417 signed CLOSED AS_LEFT serial blocks across the two eligible revisions per bay, all 24 bay orders and 16 per-serial byte reversals. For each, I checked both direct payload XOR block and payload XOR block XOR the recorded route mask. No candidate matched K04.

These are bounded cross-slot mask tests, not evidence that any of those blocks is the intended mask. I still see no defensible local K04 constructor. The only remaining route is the original coupon/native spool plus the BX25/Risk-desk source that authenticates the mask, or the native AX-7782 snapshot if it contains them.
