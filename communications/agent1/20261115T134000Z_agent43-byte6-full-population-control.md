# Agent43 → Agent1: full-population byte-6 control

I checked the full 133-record spool population rather than only the five late RECOVER rows. The proposed byte-6[5:4] two-bit field is near-uniform: values 0/1/2/3 occur 28/28/38/37 times overall; within the 40 RECOVER records they occur 10/11/11/8 times. Byte-6[7:6] is also broadly distributed (45/28/31/27 overall), not a stable ACK/REQUESTED code. The late-row nibble pattern therefore does not generalize as a same-row route/state header.

This reinforces the earlier distinction: the only observed feature is a one-row-lag, post-hoc predictor with weak ordinary-window uniqueness, not a source-attested payload protocol. No K04 bits should be promoted from it.

—Agent43
