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


## Distinct global printer-spool anchor: first ordinary 07:00 packet

The same tested implementation now accepts a second source-grounded `ordinary` mode, anchoring **PS-261003-0300 LABEL/ACK 07:00 UTC**, then searching for **PS-261003-0301 STORES/ACK 07:05 UTC** and **PS-261003-0302 STORES/ACK 07:10 UTC** as two independent, complete 16-byte holdouts. Their exact original payloads are respectively:

- `FBBBC54356483F5864BB3F06794518A5`
- `64176B6C3A91BD06B12FC0D90B3A7DB4`
- `3531D8AB362BB040E7702CE23A8D5420`

Source timestamp/job/class/destination and all three payloads are asserted against the original unchanged spool. The complete original K04 SHA256 is separately checked at every 16-byte sliding four-output window starting stage8 through stage1,048,575, without the copied selected ACK or selected target affecting the initial state fit.

| View (32-bit word packing) | Initial 2^32 trial roots | Whole 07:05 matches | Original K04 SHA256 hits | Whole 07:10 matches |
| --- | ---: | ---: | ---: | ---: |
| Forward little-endian | 2 | 0 | 0 | 0 |
| Forward big-endian | 1 | 0 | 0 | 0 |
| Reverse little-endian | 1 | 0 | 0 | 0 |
| Reverse big-endian | 0 | 0 | 0 | 0 |
| **Total** | **4** | **0** | **0** | **0** |

Original target comparisons: **4,194,272** complete whole-coupon placements (4 roots × 1,048,568 eligible sliding windows). The independently planted three-object scanner passed again, detecting output stages17,33,82 exactly. Execution is reproduced with [the single dual-anchor source SFT](../agents/agent27/k04_xoshiro128pp_label_anchor_sft.cpp) using mode `ordinary` as its final argument and bound `1048575`. The updated source remote Git blob is `7cb2bf717b2f492fd1a91ae551682a5025fb8fad`.

This independently excludes the precise **globally continuous xoshiro128++ original printer stream** from first ordinary 07:00 row to the next two ordinary five-minute packets, within one-million output positions, under the same four serializers. It offers no accepted coupon. The conclusion is conditional on a producer and output schedule absent from the surviving original documentation. The full original K04 remains missing.
