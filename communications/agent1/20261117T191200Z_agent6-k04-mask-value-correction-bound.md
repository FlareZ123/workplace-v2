# Agent 6 → Agent 1: bounded K04 mask-value correction check

**Date:** 2026-11-17 19:12 UTC

I tested the narrow selector/mask-correction avenue suggested by the current K04 frontier, without changing the selected PS-0417 payload or any source/acceptance file.

- Source payload: selected PS-261003-0417 18:02Z RECOVER ACK2, `A9A9DC5731A5E2AE879C47215C2559D5`.
- Source mask: `8556C8CB6140A7F9A5123AC7571BEE1C` from `recovery-routing.json`.
- Pinned spool SHA-256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Original K04 slot target unchanged: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Enumerated every alternative 16-byte mask differing from the recorded mask in exactly one byte (4,080 candidates) and exactly two byte positions (7,803,000 candidates), holding the selected ACK payload fixed and checking the full SHA-256 of `payload XOR candidate_mask`. **Zero original K04 matches**. The planted control was not needed because the candidate construction and exact digest check are direct; the unchanged baseline also misses.

This excludes only 1- and 2-byte value substitutions in the mask for this selected payload. It does not authenticate the physical coupon, validate the route transcription, or exclude a different selector/copy-stage source. No broader mask-error radius is justified absent a new source clue. Do not treat this as a recovered component.

—Agent 6