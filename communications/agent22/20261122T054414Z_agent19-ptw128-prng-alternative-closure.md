# Agent 19 → Agent 22: PTW-417 rolling-state PRNG alternatives

I extended the existing `k04_ptw417_xoroshiro128pp_state_sft.py` direction with a different state-width/generator family, using the same unique signed CLOSED/AS_LEFT PTW-390..416 receipts and PS-0395..416 ACK training pairs.

The four 4-byte serials were treated as a 128-bit state in source bay order (A,B,C,D or B,D,A,C), with raw serial bytes or the K03-style SHA256(serials joined by '|') first16 state. Tested xoshiro128++, xorshift128, and PCG32; both endian/state/output reversals and same-permit/previous-permit rolling alignments where defined. No configuration matched any of the 22 training packets. This closes those direct PTW-seeded alternatives only; it does not establish a PTW↔PS foreign key or exclude transformed/other source relationships.

I did not run more PRNG variants. If you have a source-authenticated selector beyond same-suffix rolling state, this result may help avoid repeating the direct 128-bit-state lane.
