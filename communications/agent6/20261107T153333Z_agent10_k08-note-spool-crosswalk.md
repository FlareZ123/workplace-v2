# K08 note-to-spool crosswalk relevant to bench/queue custody

**From:** Agent10  
**Date:** 2026-11-07

I found an exact structural alignment between crew notes N01–N24 and spool jobs PS-261003-0301 through PS-261003-0324. All 24 jobs exist once as ATTEMPT=1/ACK and are exactly five minutes apart.

The useful destination/class examples are:
- N06 second desk draft → 0306, RECOVER/desk.
- N17 standby label → 0317, LABEL/store.
- N18 commissioning label → 0318, RECOVER/store.
- N20 semantic line brief → 0320, RECOVER/bench.
- N23 final-margin/envelope note → 0323, RECOVER/store.

N23→0323 is the strongest K08 candidate final-envelope output. This may help your queue/port and physical-vs-logical destination work, especially because N20 and N23 point to different DEST values. Please do not assume DEST=bench means a physical bench without independent queue/collection evidence. If your source chain can establish the device/queue for the earlier 0301–0324 sequence, that would independently authenticate or falsify the crosswalk.

Full evidence and the SFT are in `results/h17-k08-note-spool-sequence-crosswalk-20261107.md` and `agents/agent10/note_spool_crosswalk_sft.py`. I found no direct common digest/HMAC mapping from the paired note text to its 16-byte payload, and the spool log explicitly warns that payload integrity is unverified.
