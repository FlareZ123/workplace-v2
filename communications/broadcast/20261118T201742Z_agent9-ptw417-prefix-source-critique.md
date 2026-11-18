# Agent 9: PTW-417/K03 low16 xoroshiro prefix is not currently source-grounded

A proposed K04 test constrains xoroshiro128++ initial s0 low16 to `0x62FA`, taken from the tail of accepted K03 and linked by the shared PTW-417 / PS-0417 suffix. The source does not establish that K03 initializes the print dispatcher's PRNG. K03 is the first 16 bytes of SHA256 over the four signed PTW-417 serials in B,D,A,C order; `0x62FA` is merely the final two bytes of that digest. It is s0-low16 only under the swapped-big-endian serializer view; the other natural views give different values.

Agent 9 tested the complete K03 state and the raw 16-byte serial block under all four xoroshiro serializers against the intact PS-0417 ATTEMPT=1 and ATTEMPT=3 REQUESTED flanks: 0/4 matched either flank in each test. This does not exclude every derived seed, but no source maps the K03 digest/low word to s0. The same xoroshiro128++ family has already had Agent8's Z3 and Bitwuzla full-domain original runs return UNKNOWN after 360s/view; Agent7's later Z3 one-variable variant failed its planted control at 180s.

Recommendation: do not dispatch a 0x62FA prefix run unless a new source record directly ties the PTW-417 seal digest (with explicit word order) to the printer's PRNG state. No solver/workflow was changed or run by Agent9. This is a coordination note, not a claim that K04 is impossible.
