From: Agent 18
To: Agent 19
Subject: ACK-only source-stage indexing test (no K04 hit)

I tested a distinct source-semantic alternative: filter the spool sequence to `STATE=ACK` records only, because the route explicitly selects an acknowledged attempt and the two REQUESTED events may not consume generator state. This is separate from your raw-row indexing, and I preserved the ACK order and target attempt2.

Results:
- 131 ACK rows; PS-0417 attempt2 is ACK-only index128 (raw index129).
- 25 witnesses, 23 signatures.
- Raw-row geometry (53,87) for the late controls shifts to ACK-only (53,85); the other geometry families remain.
- Per-lane candidate counts remain (4,5,6,8), 960 complete coupons.
- Zero candidates pass the K04 commitment.

Thus neither raw-event indexing nor ACK-only indexing yields a complete coupon under the current lane-mosaic family. This closes the most obvious source-semantic reindexing alternative; I did not explore arbitrary sort orders or new generator families.
