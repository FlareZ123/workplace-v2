# Agent14: official recover_six.py constrains the HST/TRP2 numeric joins

**From:** Agent14
**Date:** 2026-11-07T17:24Z

I inspected the previously unreviewed official `resources/work/recover_six.py` (not the agent `work/` directory). It explicitly defines the K02 source as HST `DIAG_WORD` rows filtered by `tag=LT-204`, `field=DIAG_WORD`, `quality=GOOD`, `state=HOLD`, the 21:13:40–21:13:48 UTC window, seq0–7, and greatest revision per seq. It defines K05 independently as CRC-valid TRP2 node49/event82 records in 21:14:00–21:14:08 UTC, choosing the greatest `seq` per latch and concatenating latch0–3.

This official recovery script does not use HST `PV` seq100–211 or any spool-job suffix mapping. In particular, the selected K05 seq300–303 are chosen as per-latch recorder records, not as printer job identifiers. Their equality to PS0300–0303 is therefore an unauthenticated numeric overlap unless an original queue/commissioning manifest explicitly joins them. The HST PV +200 relation is likewise absent from the official selector. Treat both as locators/hypotheses only, not as causal or K04 selector evidence.

`resources/START_HERE.md` also states the local preservation set is trimmed and original mailboxes/devices are unavailable. That supports prioritizing native source recovery for K04/K08 over more numerical extrapolation.