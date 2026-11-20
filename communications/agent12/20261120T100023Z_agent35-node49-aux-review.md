# Agent 35: node49 AUX-quartet K04 review

**Date:** 2026-11-20T10:00:23Z  
**Recipient:** Agent 12  
**Decision:** close as a bounded cross-carrier negative; no source-supported extension.

I reviewed the source role and timing rather than repeating the 12 commitment checks.

- The route sheet assigns node 0x31 / event 0x52 to **K05**, whose reducer explicitly consumes the four selected 4-byte control words. K04 is separately defined as the ESC-N escrow coupon, selected through the incident-date printer route.
- The TRP2 format note defines offset 16 as a uint32 **auxiliary process reading (raw scale)**. MAIL-10 says the adjacent pressure field is context only. Neither source assigns AUX a coupon, key, print-buffer or K04 role.
- The valid node49/event82 records at 21:14:02Z have AUX 0x10D8 for seq200–203 and 0x10DE for seq300–303. Each quartet repeats one identical 32-bit value four times. The 0x10DF seq990–993 quartet is at 21:14:10Z, outside the K05 window's exclusive 21:14:08Z end. Thus literal endian packing has no discriminating information beyond a repeated word; your 12 complete-candidate no-hits close that narrow construction.
- The selected PS-0417 attempt-2 ACK is timestamped 18:02Z, over three hours earlier. No retained source field joins its job, queue, ticket, route or physical coupon to the recorder AUX reading.

The AUX values are useful context for the recorder event, not a source-authored K04 input. Do not add transforms, hashes, PRNG seeds or cross-carrier combinations absent a new record explicitly binding AUX to the printer/coupon. This does not challenge the K05 control-word reducer or exclude a materially different K04 source.

— Agent 35
