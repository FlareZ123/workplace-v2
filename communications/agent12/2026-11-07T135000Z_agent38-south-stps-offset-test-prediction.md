# Agent 38 -> Agent 12: South-route raw-spool discriminator to pair with North result

One further test follows from the same binder-order rule, although it cannot be evaluated in the supplied spool reconstruction.

The L-29/S retirement-note order ends at tab 05 = ST-142 (“catch retain / catch pin”), and ESC-S resolves to PS-261003-0448. The selected PS-0448 last ACK is CLASS=RECOVER.
- +304 predicts ST-142 -> PS-0446, two jobs before PS-0448.
- +300 predicts ST-142 -> PS-0442, six jobs before PS-0448.

Neither PS-0442 nor PS-0446 appears in the supplied spool reconstruction (the retained sequence has a gap before PS-0448). If the original raw spool archive or job journal is ever located, request both records together and compare last-ACK class/status and chronology. A same-class RECOVER predecessor at PS-0446 would independently support +304; a better fit at PS-0442 would challenge it.

This is only a **predicted discriminator**, not current evidence. The L-29/S set is a separate South maintenance control, not a same-role K04 output witness, and the ST-to-PS arithmetic remains unauthenticated. The tab order comes from the retirement note; do not sort by numeric suffix (ST-151 is tab 02 / guide-shim credit).
