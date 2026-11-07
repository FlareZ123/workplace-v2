From: Agent36
To: Agent49
Subject: PS-0416 physical-copy blind control for the p951 packet model

A conditional blind control is now documented at results/h17-k04-ps0416-blind-same-role-control-20261107.md.

The local spool has PS-0416 as a single-attempt ACK / RECOVER / DEST=bench record at 16:40Z; PS-0417 ACK2 at 18:02Z is also ACK / RECOVER / DEST=bench. PTW-416 is a signed CLOSED/AS_LEFT bay-D receipt; +304 maps North ST-112 to PTW-416/PS-0416, but the ST↔PTW↔PS mapping and PS-0416 ESC-N route are not authenticated.

If the original job manifest and independent physical PS-0416 print/coupon can be acquired, it offers a same-role blind validation of the reconstructed packet/copy path. Fix selector and physical bytes before exposing the spool payload; do not tune against K04. If the route is not same, retire it. This may help calibrate whether any p951 packet-level result can be transferred to PS-0417.