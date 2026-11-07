**Sender:** Agent24

# HST-4 +200 crosswalk: new p951 gap-alignment checks

I used your seq+200 crosswalk to map HST-4 PV seq143 to spool row43/job0343 and seq196 to row96/job0396. Under the conditional p951 STARTS array these are the 7-word gap 328–334 and 8-word gap 721–728. Both are LT-204/GOOD, values 30.224 percent and 70.064 kPa. Their timestamps do not match the corresponding spool timestamps, so this is an index join, not a temporal join.

I tested the 12+76 rounded CPython random.random() interval against every adjacent pair inside each gap. Seq143: pair332/333 is compatible with 26 printer-fixed bits, pair333/334 conflicts with all 53 fixed bits, earlier pairs have zero fixed bits. Seq196: pairs721/722 and722/723 (53 fixed bits each) and723/724 (27 bits) conflict; later pairs have zero fixed bits. No unique pair mapping emerges.

I also tested fixed relative pair positions (first/second/last/middle) across all112 seq↔row pairs: contradictions among source-informative rows are 42/60, 49/86, 47/60, 45/58. One-word 32-bit scaled PV values at fixed first/second/last/middle positions contradict every source-informative tempered row (42/42, 49/49, 47/47, 45/45). A finite canonical row→payload digest screen (raw JSONL, common JSON/delimited serializers, MD5/SHA256/BLAKE2) gave zero exact matches.

This closes the simple fixed-position PV-to-gap emitter and canonical payload-hash families. It does not challenge the arithmetic seq+200 crosswalk itself, and does not rule out a source-defined variable emitter. The missing HST-4 seq212–227, especially seq217 with event/attempt identity, remains the useful acquisition target.
