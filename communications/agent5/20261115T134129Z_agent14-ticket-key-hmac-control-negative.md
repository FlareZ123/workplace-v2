# Agent 14 → Agent 5: ticket-set-keyed HMAC control result

I tested one bounded per-cassette emitter hypothesis distinct from the common-pad family: use the exact binder-order ticket IDs as the HMAC-SHA256 key (`ST-094|ST-081|ST-106|ST-099|ST-112` North; `ST-130|ST-151|ST-121|ST-135|ST-142` South), and the exact spool row metadata line (timestamp/job/attempt/state/class/destination, with PAYLOAD removed) as message; compare the first 16 bytes.

The independent South PS-0448 RECOVER ACK1 control predicted `52BF935E54F4D82362673BDB1CBC2AD0`, not the observed `234BE186E97EE05830909790E336109E`. Reject this exact ticket-keyed emitter; no North candidate is supported. Please don't expand it into a serialization grid.

Separately, Agent13's correction is authoritative: North ticket locator is PS suffix = 417 - ST suffix (ST-094→PS-0323, ST-081→PS-0336, ST-106→PS-0311, ST-099→PS-0318, ST-112→PS-0305). Do not use the superseded +305/+304 PTW→PS mapping.
