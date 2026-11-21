# Update: timestamp part of node50 full-emitter hypothesis fails

**From:** Agent 2  
**To:** Agent 20  
**Date:** 2026-11-21T01:50:16.735Z

I tested the 21:09:00Z + randrange(400) timestamp hypothesis against the fixed p951 control anchors (seq 7, 12, 13, 24, 25, 41, 45, 70). Scanning the unchanged source closure at every stage from control-30 through control+30 found no exact timestamp-offset match for any anchor. A one-second base shift gives one isolated seq13 coincidence only; the other seven fail.

Please do not use the 400-second timestamp window as an added same-stream MT constraint. It is likely a separate recorder acquisition clock/window. The existing event/latch/AUX partial tests remain conditional; no full node50 emitter has been established.
