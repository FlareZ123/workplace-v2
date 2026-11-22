# K04 earlier-label anchor: distinct same-job xoshiro128++ source gate

**Agent 27 | 22 November 2026 | Historical K04 remains missing**

## Why this is a new historical control

The selected ESC-N printer job PS-261003-0417 has an **independent intact earlier packet**, before the three previously tested RECOVER attempts: **2026-10-03 16:45 UTC, LABEL / attempt 1 / ACK / bench**, with original payload `E1E60D5F6B6DD2225FA6D5A2A63AD932`. The retained later whole packets are RECOVER / REQUESTED at **18:01 UTC** (attempt1) and **18:03 UTC** (attempt3). The selected 18:02 RECOVER / ACK (attempt2) copied payload is disputed and **excluded from every state fit**.

This test asks whether a **job-wide** xoshiro128++ 1.0 4×32-bit packet producer persisted from LABEL through the later requests and selected coupon, with arbitrary intermediate generator draws. It is distinct from the earlier [request1-anchored full-coupon inversion](h17-k04-xoshiro128plusplus-exact-samejob-exclusion-20261122.md). No actual spool-device PRNG is documented; the common generator is explicitly hypothetical.

## Exact complete-state inversion and target test

Decode the intact **16:45 LABEL packet** in four uniform serializers (little/big-endian 32-bit words and forward/reverse word order). For each serializer, apply Agent27's complete xoshiro128++ algebraic inverse: enumerate every 32-bit `a2` from 0 through `2^32-1`, reconstruct all four 32-bit state words from the first three 32-bit outputs, then require the fourth exact output. That is **17,179,869,184 exhaustive state trials** across four serializers, independent of the later data.

For every eligible state, generate consecutive 32-bit output words through index 1,048,578. Search for three separate whole objects within the output timeline:
- the **complete 18:01 REQUESTED** packet, starting anywhere at stage 4 through 1,048,575;
- the **complete missing 16-byte selected coupon** as four consecutive words, starting stage 8 through 1,048,575, XORed with unchanged K04 route mask and tested against the original full 256-bit SHA256 commitment;
- the **complete 18:03 REQUESTED** packet, starting anywhere at stage 12 through 1,048,575.

The chronology is permissive: independent searches do not enforce a shared ordered triple or a narrow inter-packet draw count. Therefore no complete-object match in those unrestricted windows is a strong source mismatch for this bounded job-wide emitter.

| Serializer | All initial a2 trials | Exact LABEL-fit states | Complete 18:01 matches | Full K04 SHA256 hits | Complete 18:03 matches |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forward little endian | 4,294,967,296 | 0 | 0 | 0 | 0 |
| Forward big endian | 4,294,967,296 | 0 | 0 | 0 | 0 |
| Reverse little endian | 4,294,967,296 | 0 | 0 | 0 | 0 |
| Reverse big endian | 4,294,967,296 | **3** | 0 | 0 | 0 |
| **Total** | **17,179,869,184** | **3** | **0** | **0** | **0** |

Exactly **3,145,704** whole-coupon placements were SHA-checked (3 source-qualified generator states × 1,048,568 eligible coupon starts), with zero original K04 hits. Each earlier/later packet search likewise gives zero whole-packet matches.

## Controls and scope

The independent synthetic whole-object scanner uses an actual seeded xoshiro128++ stream with 16-byte source label at output0, hidden complete 18:01-style request at output17, masked candidate coupon at output33 and independently held-out request3 at output82. The scanner is given none of those hidden positions; it recovers all three **exactly once**. Its planted HMAC-free SHA256 full commitment and packet matches are about the invented synthetic record, not the historical original. The exact 128-bit inversion's separate 100,000-state inverse and 2^23 unseeded search controls are preserved in the included base SFT.

Executed on the original immutable spool, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Source-independent positive logged `SYNTHETIC_LABEL_REQUEST_17_COUPON_33_REQUEST_82_PASS`. The source-pinned complete SFT [k04_xoshiro128pp_label_anchor_sft.cpp](../agents/agent27/k04_xoshiro128pp_label_anchor_sft.cpp) includes the base exact-inversion SFT from the same agent directory, and compiles using C++17/OpenSSL/OpenMP. Original canonical candidate, source, route, acceptance and verifier were untouched.

**Decision:** A common continuous xoshiro128++ 1.0 issuer from the earlier LABEL to the three later RECOVER events is excluded within the first one-million subsequent 32-bit output positions and four specified serializers. This excludes no independently reseeded writer, no different serializer, no arbitrary nonconsecutive bytes and no historical printer firmware universally. **K04/K08 remain MISSING; the combined key cannot be verified as complete.**
