# Agent 25 — K04 job-paired native spool commitment bridge

I composed the existing SPL/SHD pairer with the existing K04 exact 16-byte commitment-window scanner. The new `agents/agent25/k04_native_spool_commitment_bridge.py`:
- pairs SPL/SHD only by exact container, parent path and normalized filename stem;
- requires the literal `PS-261003-0417` job ID in the paired SHD (ASCII or UTF-16LE);
- scans the paired SPL's raw16 and supported encoded 16-byte windows against the pinned K04 SHA256, checking direct component and exact route-mask XOR;
- reports source hashes, offsets and candidate bytes without extracting or modifying source files.

The planted payload-at-offset-6 control and wrong-job decoy pair passed in [run 45094353923](https://github.com/FlareZ123/workplace-v2/actions/runs/45094353923). The supplied ZIP contains no native SPL/SHD, so no real component was recovered. The SHD literal and pair key are still only candidate job association; independent evidence must establish RECOVER/bench/ACK attempt2.

Use the bridge only on an already-authorized original spool directory/archive; preserve the SPL/SHD pair and queue metadata. [Method and limits](../../results/h17-k04-native-spool-commitment-bridge-20261123.md).
