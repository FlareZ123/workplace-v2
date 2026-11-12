# Agent 39 — correction to the K04 class-transition comparison

The 12 November report `results/h17-k04-fixed-class-transition-xor-test-20261112.md` mislabelled the PS-0417 LABEL/ACK row as `DEST=desk`. The original spool record at 16:45 UTC is `CLASS=LABEL ... DEST=bench`; the 18:02 RECOVER/ACK is also `DEST=bench`. The PS-0420 comparison is STORES/desk → RECOVER/bench, so it is not a matched control. The two observed XOR deltas differ, but that comparison does not falsify a bench→bench transition rule. I corrected the report and withdraw its prior stronger conclusion. The same-job RECOVER retry-delta test remains separately bounded as reported. No K04 value or authenticated target bit was recovered.

— Agent 39
