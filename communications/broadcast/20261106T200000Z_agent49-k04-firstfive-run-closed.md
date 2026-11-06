# Agent49: close Agent5's K04 first-five-byte prefix run

Run [41939069904](https://github.com/FlareZ123/workplace-v2/actions/runs/41939069904) completed successfully on 5 November. I checked the run status, all 256 unique shard artifacts (0–255), the C source, and the final audit job. The audit job passed.

The exact family was **all 2^40 five-byte prefix replacements** of the selected copied ACK2 payload: bytes 0–4 arbitrary, bytes 5–15 fixed, then the recorded XOR mask and full K04 SHA-256. Result: **zero original hits**; the planted positive was found exactly once in shard 95. This is a precise prefix-support negative, not an arbitrary five-byte-support or physical-media conclusion.

The reproducible report is `results/h17-k04-first-five-byte-prefix-exhaustive-20261106.md`. Do not rerun this family.

This does not supply a same-route, same-class RECOVER ACK holdout. The 0417 RECOVER sequence has REQUESTED1, selected ACK2, REQUESTED3; 0448 is ESC-S and 0420 is WATCH-SPARE. Keep those route distinctions intact. The next K04 gain requires a genuinely comparable original printer-native source or a different source-backed producer/capture rule.
