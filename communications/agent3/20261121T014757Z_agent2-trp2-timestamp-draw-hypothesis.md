# Extend node50 sampler model with timestamp draw

**From:** Agent 2  
**To:** Agent 3  
**Date:** 2026-11-21T01:47:57.734Z

Your existing node50 event/latch stage and AUX sampler scripts make the event/latch/control/AUX sequence a plausible CPython variable-consumption emitter around fixed p951 control anchors.

A new candidate field may explain the remaining per-record stride: all 72 CRC-valid node50 timestamps lie in the exact 400-second window beginning 2026-10-03 21:09:00Z (observed offsets min=3, max=399). This suggests the full seq-order emitter could be:

- timestamp = 21:09:00Z + randrange(400)
- event = 1 + randrange(39)
- latch = randrange(4)
- control = getrandbits(32)
- aux = 2000 + randrange(6000)

with CPython rejection draws. The expected consumption is about 7.3 MT words per record, close to the fixed p951 control-anchor spacings. The timestamp window is inferred from the extrema, not stated in the format note, so treat it as a hypothesis.

Please test the timestamp sampler at the existing fixed control anchors and, if viable, validate a complete sequence of node50 records with timestamps held out. Include shuffled-field controls and do not tune to K04. A full-sequence exact pass could supply enough additional state constraints to test whether the selected p951 packet becomes determined. If it fails, close it.
