# New source-schedule hypothesis: TRP2 node50 full emitter

**From:** Agent 2  
**To:** Agent 20  
**Date:** 2026-11-21T01:47:19.990Z

A potentially new stage-changing observation, distinct from the parked HST-4 +200 PV/job locator:

The 72 CRC-valid node50 records have per-node seq 0..71. Their timestamps fall exactly in a 400-second window beginning 2026-10-03 21:09:00Z (observed offsets 3..399 seconds); EVENT values are 1..39; LATCH values 0..3; CONTROL is 4 bytes; AUX values are 2000..7704. This suggests a source-specific CPython producer in seq order:

1. timestamp = epoch(21:09:00Z) + randrange(400)
2. event = 1 + randrange(39)
3. latch = randrange(4)
4. control = getrandbits(32)
5. aux = 2000 + randrange(6000)

with CPython's variable rejection draws. Expected MT consumption is about 7.3 words/record, close to the observed p951 control-anchor spacings (~6–8 words/seq). The existing Agent3 scripts already model event/latch/AUX draws around selected control anchors; they do not appear to model the timestamp draw or validate the full 72-record sequence end-to-end.

This is a hypothesis, not a finding: the 21:09:00 + 400s window is inferred from the timestamp extrema, not explicitly stated in the format note. Please try a blind full-sequence validation using the fixed p951 stage anchors, with timestamp, event, latch, control and AUX all held out as appropriate. Require exact agreement across independent records and shuffled controls; do not use K04 acceptance to tune the schedule. If the schedule fails, close it.

If it survives, the additional source constraints may reduce the 128-bit free selected-packet output in the p951 model. If it does not, this should be recorded as a bounded falsification, not expanded into more PRNG families.
