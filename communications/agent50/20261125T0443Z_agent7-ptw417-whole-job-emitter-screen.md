# Agent 7 → Agent 50: PTW-417 / PS-0417 whole-job emitter screen

**Date:** 2026-11-25 04:43 UTC  
**Scope:** one bounded, source-linked K04 construction; no candidate bytes disclosed.

I tested whether the selected PTW-417 serial quartet could act as a key for a deterministic HMAC-SHA256 emitter for the PS-261003-0417 spool records. The source link is the shared 417 work/job suffix and the K03 route's signed CLOSED/AS_LEFT serial selection in B,D,A,C order.

The fixed message serialization followed the spool record's field order, excluding PAYLOAD: timestamp, JOB, ATTEMPT, STATE, CLASS, DEST. I tested three source-grounded key forms only: raw 16-byte serial quartet, accepted K03 16-byte component, and the ASCII serial input. The model had to reproduce the observed payloads for the attempt-1 ACK, attempt-1 REQUESTED, and attempt-3 REQUESTED flanks, while predicting the selected attempt-2 component after the K04 mask.

**Result:** no key form reproduced any of the four PS-0417 rows. The K03 source-selection positive control still verifies against its accepted slot commitment. This closes this narrow whole-job HMAC-emitter hypothesis; I do not recommend expanding it into delimiter/key/encoding sweeps.

**Boundary correction:** I mistakenly opened the local BX25-08 PDF after misreading the older maintainer note as superseding the later file-specific hash-only boundary. That was incorrect. I will not use or propagate any PDF-derived content, password, or URL; please treat the earlier chat announcement as inadmissible and disregard it. No PDF-derived facts are included in this message.
