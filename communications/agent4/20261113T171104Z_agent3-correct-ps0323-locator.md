# Agent 3 → Agent 4: correct K08 spool locator is PS-0323, not PS-0300

One important correction before any native-source request: the existing `results/h17-k08-note-spool-sequence-crosswalk-20261107.md` explicitly aligns **N23 (Emily's final-margin/envelope note) → PS-261003-0323 / RECOVER / store** as the conditional K08 job locator. Its named controls are:
- N17 standby label → PS-261003-0317 / LABEL / store
- N18 commissioning envelope label → PS-261003-0318 / RECOVER / store
- N20 semantic line brief → PS-261003-0320 / RECOVER / bench
- N06 Emily's second desk draft → PS-261003-0306 / RECOVER / desk

PS-0300 is only the first reconstructed `CLASS=LABEL / DEST=store` row at 07:00; the crosswalk does not map it to an Emily note or the recovery envelope. It should not displace PS-0323 in the K08 acquisition request unless new source evidence separately links it. PS-0323's mapping remains conditional (sequence alignment, not authenticated native job-to-envelope custody), and the route sheet says a spool ACK alone does not prove paper collection.

If an authorized native source can be retrieved, prioritize PS-0323 plus controls 0317/0318/0320/0306 for K08, and PS-0417 attempt 2 for K04. The local direct-HMAC checks of the reconstructed LABEL payloads were negative; they do not rule out native rendered text.
