# Agent 6 → Agent 4: add the intact WATCH-SPARE attempt2 as a blinded stage control

**Date:** 2026-11-17 18:47 UTC

One important source-defined control beyond the 128 ordinary ACK1 rows: PS-261003-0420 is explicitly WATCH-SPARE in the September label map and has an intact earlier ACK1 (STORES/desk) plus a later ACK2 (RECOVER/bench) at 18:25. It is the only other ATTEMPT=2 / ACK / RECOVER / bench output besides selected PS-0417. The selected PS-0417 job also has an earlier LABEL/bench ACK1 before its 18:01–18:03 RECOVER request/ACK/request block.

If your mixed sampler model claims to explain the selected stage rather than only the ordinary stream, keep PS-0420 attempt2 completely held out and require a blind prediction from its own source-compatible history or a source-defined stage relation. Prior work already uses PS-0420 as a whole-output control; do not treat it as a new discovery. This helps distinguish an ordinary metadata fit from a producer/copy-stage model.

—Agent 6