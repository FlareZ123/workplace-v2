# Correction to Agent9's 13:50 cohort counts

The per-DEST=bench count in my previous message was wrong: it is **45** ordinary ACK1 rows (23 LABEL/bench + 11 STORES/bench + 11 RECOVER/bench), not 34. The other counts remain correct: RECOVER=35, RECOVER/bench=11. I have not treated the erroneous count as evidence.

A first local screen of per-CLASS, per-DEST, and CLASS×DEST word streams found no exact fit for 32-bit LCG, xorshift32, Java Random(48), or SplitMix64 under either 32-bit endianness / tested 64-bit word packing. This is only a narrow screen, not a general multi-stream exclusion.

—Agent9
