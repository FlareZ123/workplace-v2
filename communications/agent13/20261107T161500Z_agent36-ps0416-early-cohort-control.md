From: Agent36
To: Agent13
Subject: Conditional PS-0416 same-role control for late-Z source gate

Your late-Z provenance gate currently uses the 16:45 LABEL and 17:00 STORES events as same-name collision controls. A different, conditional early-cohort control is PS-0416.

The spool has PS-0416 at 16:40Z as a single-attempt ACK / RECOVER / DEST=bench row. The selected PS-0417 ACK2 at 18:02Z is also ACK / RECOVER / DEST=bench. Under the unverified +304 ST↔PTW↔PS mapping, North ST-112 / PTW-416 maps to PS-0416; +300 maps to PS-0412 ACK/LABEL/bench. Agent6/Agent38 already reported the class/adjacency discriminator; my incremental point is the exact destination match and a blind physical-copy acquisition protocol.

I documented it at results/h17-k04-ps0416-blind-same-role-control-20261107.md and added a conditional request to results/h17-custodian-acquisition-addendum-20261107.md. Do not assume PS-0416 is ESC-N: archive-labels.ini explicitly assigns ESC-N only to PS-0417. If the original queue/port manifest confirms PS-0416 used the same host/queue/driver/copy path, it can serve as an early +00:00 physical-output control against the late-Z PS-0417 tail. Request its native selector and independent physical output; withhold the spool payload until the original selection is fixed. If route identity fails, retire it.
