# K04: UUIDv7 complete coupon with unknown 12-bit rand_a, event-local milliseconds

**Agent 9 | 22 November 2026 | Original K04: 0/1,474,560,000 full SHA-256 matches. K04 MISSING.**

## Target-bearing hypothesis

The copied ESC-N / PS-261003-0417 RECOVER attempt-2 ACK at 2026-10-03T18:02:00Z is an unauthenticated 16-byte printer buffer. Its source suffix bytes 8..15 are \`879C47215C2559D5\`; that leading suffix octet has the RFC 9562 UUID variant \`10\` bits. The source **does not state that its coupon is a UUID** or establish the suffix's physical integrity. The RFC 9562 v7 *conditional producer hypothesis* assumes:

- coupon bytes 0..5 encode a 48-bit Unix-millisecond timestamp between **18:01:00.000Z inclusive and 18:04:00.000Z exclusive** on 3 October 2026;
- byte 6's leading nibble is UUID version 7;
- **all 4,096 values of the remaining 12-bit \`rand_a\`** in bytes 6..7 are unconstrained and exhaustively varied;
- bytes 8..15 remain exactly the copied source suffix, whose 0x87 octet already has the RFC UUID variant;
- two serializers are tested: RFC/network byte order, or Windows GUID reversal of fields 4+2+2 with the suffix unchanged.

Construct every full sixteen-byte coupon, XOR it against the **unchanged** original K04 route mask \`8556C8CB6140A7F9A5123AC7571BEE1C\`, and compare the **complete 256-bit SHA-256** of the resulting sixteen-byte component against original target \`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0\`. No truncated hash, source-selected seed, or copied first-eight-byte hint is used.

This extends, rather than repeats, Agent46's 4 November **3,240,000** complete timestamp-prefix UUIDv7/ULID pilot: that study patched the copied first-eight field's version and tested timestamp/time serializers while keeping the remaining copied random field; the present study frees **the entire 12-bit \`rand_a\` field**. Do not interpret this selected-only extension as reversing the earlier failure of ordinary intact RECOVER packets to exhibit timestamp-ID prefixes.

Official codec reference: [RFC 9562 §5.7](https://www.rfc-editor.org/rfc/rfc9562.html#section-5.7). Source pins: original \`spool-reconstruction.log\` SHA256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`; route JSON \`f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5\`; acceptance \`681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f\`. The C++ reproducer contains the original pinned coupon, mask and target as literals, and does not rewrite any source.

## Complete local execution

Reproducer: [\`agents/agent9/k04_uuidv7_rand_a_sft.cpp\`](../agents/agent9/k04_uuidv7_rand_a_sft.cpp). C++17/OpenSSL/OpenMP-free std::thread implementation runs 4 threads. Uses the SHA256 compression block for an exactly 16-byte input with standard padding, with the complete output compared against the original target. Independent OpenSSL \`SHA256()\` controls compare every digest word for four sample coupons in each serializer. Each shard also plants one full coupon \`rand_a=0xACE\`, Windows GUID order, \`timestamp=start+13ms\`, sets an independent synthetic complete SHA256 target and **must find exactly one synthetic match in the actual search loop**.

| Exclusive timestamp window (UTC, 3 Oct 2026) | Complete original candidates | Original matches | Synthetic matches | Seconds |
| --- | ---: | ---: | ---: | ---: |
| 18:01:00–18:02:00 | 491,520,000 | 0 | 1 | 7.703 |
| 18:02:00–18:03:00 | 491,520,000 | 0 | 1 | 7.709 |
| 18:03:00–18:04:00 | 491,520,000 | 0 | 1 | 7.844 |
| **Total** | **1,474,560,000** | **0** | **3** | **23.256** |

Each source shard returned exit 0 and the precise expected count \`60000 timestamps × 4096 rand_a × 2 serializers\`, with one planted positive and zero original matches. The initial 1,000ms pilot also passed: 8,192,000 complete checks, zero original hits, one synthetic positive.

## Decision

Under the timestamp-window/RFCv7/copied-suffix hypothesis, **no complete accepted K04 coupon exists**, even when the copied bytes 6..7 are wholly distrusted. This excludes a larger, well-defined **selected-only** 12-bit field than previous time-ID pilots. It does **not** exclude other timestamp ranges, a different GUID layout, damage in the copied final eight bytes, other producers, or a physical coupon with no timestamp-ID structure. The selected UUIDv7 issuer is speculative; no original physical K04 bit is authenticated by this negative. There is no K08 word recovered, and the six previously accepted components and original verifier remain untouched.

Do not broaden to arbitrary time windows, random suffix donors or unrelated UUID fields without a source-authored time/issuer relationship; the ordinary source timestamp-ID controls already failed.
