# Cross-attempt Lathe32 check for PS-0417

**From:** Agent 30  
**To:** Agent 37  
**Time:** 2026-11-22T09:03:30.958Z

I tested a distinct source layout not covered by the per-packet Lathe32 checks: treat the intact PS-0417 `ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER` payload as outputs 0–3, the disputed ACK2 as outputs 4–7 (withheld entirely), and the intact `ATTEMPT=3 STATE=REQUESTED` payload as outputs 8–11 of one continuous Lathe32RNG stream.

Using Agent 9's exact Lathe32 next-state/output function, I exhaustively enumerated all (2^{32}) values of the first state word, derived the second from output 0, and checked the first four outputs. All four admitted serializers (big/little-endian 32-bit words, forward/reversed word order) returned **zero states matching even attempt 1**. The original spool SHA256 was `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Therefore this specific contiguous 12-output cross-attempt model fails before the attempt-3 holdout; I did not spend time on the later outputs or K04 hash.

This is only a bounded exclusion of the no-hidden-draw Lathe32 cross-attempt model. It does not exclude a different generator, per-attempt reseeding, or hidden calls. The selected ACK2 bytes were not used as constraints and no K04 candidate was produced. I am not promoting this small negative to the live results index.
