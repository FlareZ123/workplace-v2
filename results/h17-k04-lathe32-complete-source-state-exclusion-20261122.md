# K04: exact 64-bit xoroshiro64++ / Lathe32RNG packet issuer fails intact source holdouts

**Agent 9 | 22 November 2026 | Five original intact ACK packets, 20 serialization views; zero complete-output matches.**

## Distinct issuer architecture

A smaller 64-bit-state printer producer was tested: the published Lathe32RNG, also called xoroshiro64++. Each 16-byte packet is hypothetically four consecutive 32-bit outputs. The author-supplied [Java nextInt implementation](https://github.com/yellowstonegames/SquidLib/blob/master/squidlib-util/src/main/java/squidpony/squidmath/Lathe32RNG.java) has 32-bit state constants (13,5,28) and an output scrambler rotating ten bits:

```text
y = rotl32((a+b) modulo 2^32,10) + a modulo 2^32
t = a XOR b
a' = rotl32(a,13) XOR t XOR (t << 5)
b' = rotl32(t,28)
```

Given only the first observed 32-bit output y0, every proposed state word a uniquely determines b:

```text
b = rotr32((y0 - a) mod 2^32,10) - a mod 2^32
```

Thus the entire 64-bit state is exhaustively inverted in exactly 2^32 enumerations of a. Reject states whose following output differs from observed word1. Replay independently withheld output words2 and3; require complete four-word packet equality. No hidden seed, K04 target, disputed ACK2 or word2/3 enters inversion.

Original input: resources/evidence/print/spool-reconstruction.log, SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. Select the first five ordinary ACK attempt1 packets PS-0300..0304, withholding selected K04 ACK2 entirely. Four serializers per packet: whole-word big/little endian, and four-word forward/reverse order.

## Completed original source and planted controls

Reproducers: [native C++17 state inverse](../agents/agent9/k04_lathe32_64bit_complete_inverse.cpp) and [SHA-pinned five-packet runner](../agents/agent9/k04_lathe32_original_holdout_sft.py). The source-independent planted state (C0FFEE17,BADA551E) yields four emitted 32-bit words 2A0CC406 8D47BBA1 F9DEA1FD BC1D55D2; the exact 2^32-state loop recovered this original planted state and both withheld outputs, once. An initial source-independent control failed due to repeating output1 in the holdout check; this mistake was corrected before the original-source tests.

| Original source set | Views | Exact states enumerated | Complete four-word matches |
| --- | ---: | ---: | ---: |
| PS-0300..0303, all serializers | 16 | 68,719,476,736 | 0 |
| PS-0304, all serializers | 4 | 17,179,869,184 | 0 |
| **Total** | **20** | **85,899,345,920** | **0** |

Across the 20 complete source views 18 proposed states survived the first-two-word constraints. None produced a complete matching four-word original packet. Every view counted all 2^32 states, with successful process exit. Four-thread and eight-thread timings on the local executor varied; on eight threads, each 2^32 case took approximately 1.6–2.1 seconds. These 85.9 billion are source-only state enumerations, not original K04 commitment comparisons.

## Interpretation

The exact **single 64-bit state, four consecutive direct Lathe32RNG 32-bit outputs per physical packet** model does not explain these intact printer packets under any of the four admitted serializers. This is an exhaustive state-model negative, not a solver timeout. The company sources do not identify Lathe32RNG as the actual printer producer; exceptional-only emitters, omitted calls and different serialization would need new models and controls. This branch should stop rather than transfer a failed issuer to selected ACK2.

No selected physical K04 coupon or K08 exact final words were recovered. The original six accepted components and verifier remain unchanged; combined REC8/1 remains incomplete.
