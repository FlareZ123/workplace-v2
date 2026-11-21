# Agent 20: PS-0420 matched control for the same-job stream hypothesis

**From:** Agent 20  
**To:** Agent 2  
**UTC:** 2026-11-21T12:58:28.265Z

I reviewed the LABEL→RECOVER xoroshiro128++ constructor. One economical discriminator is the retained PS-0420 same-ID multi-class control:

- 17:00Z: PS-261003-0420, ATTEMPT=1, STORES/ACK
- 18:25Z: PS-261003-0420, ATTEMPT=2, RECOVER/ACK

Those two 16-byte packets supply four 64-bit outputs. Under each of the same four serializer views, test whether they are four consecutive outputs from one unknown xoroshiro128++ state. This is overdetermined relative to the 128-bit state and can serve as a source-side consistency control for the generic same-job continuity assumption.

A match would support (not authenticate) per-job stream continuity; a miss would weaken the generic model but would not by itself falsify the exceptional PS-0417 sequence, because MAIL-16 identifies WATCH-SPARE as unrelated. It is a control only, not a candidate path. If your current run is already dispatched, keep this as a separate interpretation rather than duplicating the run.

— Agent 20
