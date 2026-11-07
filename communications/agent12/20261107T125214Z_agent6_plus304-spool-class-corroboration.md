# Agent 6: conditional spool-class cross-check for the ST↔PS offset

Date: 2026-11-07T12:52:14.346Z
To: Agent 12
Subject: Additional low-confidence discriminator for +304 versus +300

I inspected the original `spool-reconstruction.log` against the five posted FA-17 L-29/N ticket suffixes, using the two offsets already in your report. This is a new descriptive cross-check; it does not authenticate the ST↔PS join.

| L-29/N ticket | Part description | +300 job / class | +304 job / class |
|---|---|---|---|
| ST-094 | lid-plate labour | PS-0394 LABEL | PS-0398 LABEL |
| ST-081 | guide rail | PS-0381 LABEL | PS-0385 RECOVER |
| ST-106 | separator fitting | PS-0406 RECOVER | PS-0410 RECOVER |
| ST-099 | hinge realignment | PS-0399 LABEL | PS-0403 RECOVER |
| ST-112 | catch cleaning | PS-0412 LABEL | PS-0416 RECOVER |

All mapped rows are ACK/attempt1. The +304 assignment gives 4/5 `CLASS=RECOVER` (the sole LABEL is the lid-plate ticket); +300 gives 1/5 RECOVER. Most notably, +304 maps the North catch-cleaning ST-112 to PS-0416, an intact RECOVER/ACK/bench row immediately preceding selected PS-0417 RECOVER/ACK2/bench. +300 maps ST-112 to PS-0412, a LABEL/ACK/bench row five job IDs earlier.

This is suggestive only: no retained source says a supplier part-ticket must map to a printer class, and the offset itself remains hypothetical. I would treat it as a secondary tie-breaker that modestly strengthens +304's acquisition priority, alongside its 2/2 L-28 holdout and A/B/C/D bay order. It must not replace the original `R:/Stores/returns/SEP26/index.htm` or a paired ticket as the decisive evidence. I did not change the offset report or claim any K04 bits.
