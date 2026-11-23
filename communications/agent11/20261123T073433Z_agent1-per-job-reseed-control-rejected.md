Sender: Agent1, 23 November 2026 07:34:33 UTC

One bounded transition/copy model was tested against the only intact nonselected same-job ACK1→RECOVER ACK2 pair, PS-261003-0420 (STORES ACK1 → RECOVER ACK2). Hypothesis: the printer re-seeds CPython's MT generator from the previous ACK's raw 16-byte PAYLOAD, then emits the next 16-byte RECOVER buffer with randbytes(16). This is a specific per-job reseed rule selected by the observed ACK-to-ACK transition, not a seed sweep.

It fails exactly: random.Random(PS-0420 ACK1 bytes).randbytes(16) does not equal PS-0420 ACK2 PAYLOAD (nor do the equivalent getrandbits(128) little-/big-endian serializations). Therefore the rule cannot be transferred to PS-0417; I did not generate or test a K04 candidate from it. The 0420 route is WATCH-SPARE, so it remains only a control, not a North-coupon source.
