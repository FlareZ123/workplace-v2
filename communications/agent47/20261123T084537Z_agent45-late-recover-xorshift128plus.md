# Agent 45: bounded late-RECOVER xorshift128+ stream test

A new source-selected alternative was tested for K04. The five late `Z`-timestamp `CLASS=RECOVER` rows form the event sequence: PS-0417 REQUESTED1, PS-0417 ACK2 (withheld target), PS-0417 REQUESTED3, PS-0448 ACK1, PS-0420 ACK2. The model hypothesis was that these were consecutive 16-byte packets from one global V8/JavaScript-style xorshift128+ stream (two 64-bit outputs per packet).

To avoid fitting the target, I constrained only the first packet (outputs 0–1) and last packet (outputs 8–9), leaving request3 and PS-0448 as holdouts and ACK2 completely withheld. I tested all four 64-bit serialization views (big/little endian, normal/reversed word order). All four were UNSAT in 1.3–2.1 seconds. Therefore no xorshift128+ state can produce even those two endpoint packets as a contiguous stream in any tested view; this global-stream hypothesis is closed. No target payload, mask, or K04 commitment was used.

This is distinct from the earlier xoroshiro128++ output/state tests and does not rerun the 64-case K07-prefix matrix.