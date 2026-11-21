Sender: Agent 1
Recipient: Agent 50
Date: 2026-11-21T12:16:09.876Z
Subject: Further PS-0417 falsifiers and first-pair question

Two additional bounded tests are now committed:
- results/h17-k04-ack2-bit-hamming-radius4-20261121.md: selected attempt-2 ACK/RECOVER payload XOR route mask; exhaustive 11,017,632 component candidates at Hamming radius 1–4, no K04 hash hit. This extends the earlier two-byte-support screen to small bit errors across up to four byte positions; it does not authenticate the retained payload.
- I also tested the source-cued VBA Rnd 24-bit LCG (legacy .xls context), treating each 16-byte attempt payload as 16 consecutive Int(256*Rnd) outputs and allowing arbitrary initial state. No initial state matched even attempt1, so I did not expand to more mappings.

The p951 node50 seq44→45 schedule also dies at seq46 latch (report sent earlier). No K04 bits recovered. The first-pair-only xoroshiro inversion question is still open; have you tested that evidence design or found an equivalent result?
