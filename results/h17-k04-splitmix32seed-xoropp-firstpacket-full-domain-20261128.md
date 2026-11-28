# K04: exhaustive 32-bit startup seeds for canonical SplitMix64 → xoroshiro128++ first packet

**Agent 31 · 28 November 2026 · original-source producer exclusion, not a recovered K04 coupon**

## Distinct original-target-reaching hypothesis

The 28 November K04 program has exact but expensive seed-free first-packet xoroshiro128++ inversion. That mathematical model allows arbitrary 128-bit initial states and has produced several states that fit one untouched PS-0417 printer request. A more restrictive, historically conceivable *startup path* is a standard 32-bit application seed expanded to two native 64-bit state words by consecutive SplitMix64 outputs, then two xoroshiro128++ 1.0 outputs serialized into the first PS-261003-0417 REQUESTED packet. A full first-packet match would construct the entire issuer state and allow directly checking complete later coupon windows against the original K04 commitment.

This screen exhausts **every 32-bit seed value**, not a list of dates/job IDs. Its source connection remains hypothetical: neither the vendor's actual generator nor 32-bit seeding is documented. This is not a new inference of producer authenticity.

## Frozen exhaustive construction

For seed `s`, initialize the SplitMix64 counter to either unsigned zero-extension of `uint32(s)` or signed extension of `int32(s)`; signed extension duplicates unsigned state for `s < 2^31`, so those duplicate assignments are omitted. Compute two consecutive SplitMix64 outputs using the canonical Weyl increment and mix multipliers. Test both orders as the xoroshiro128++ initial state `(a,b)`. The standard first output is `ROTL64(a+b,17)+a mod 2^64`; the subsequent output uses the standard `(49,21,28)` transition.

Compare the exact **two native 64-bit output words** to the sole intact `JOB=PS-261003-0417 ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER` retained packet under four whole-packet layouts: big/little endian within each word and AB/BA word order. No ACK2 byte, optional third request, original K04 commitment or target has any role in fitting a seed. A full fit would be an independently replayable state and could then drive complete target-window tests.

The record comes from the original non-PDF `resources/evidence/print/spool-reconstruction.log`, SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` (locally checked before the run). The exact source bytes and original target are never compiled into the runner or printed.

## Executed results

| Measure | Completed |
| --- | ---: |
| Base 32-bit seeds | 4,294,967,296 |
| Additional nonduplicate signed-extension assignments | 2,147,483,648 |
| Initial state orders per seed | 2 |
| **Fully enumerated seed/state-order assignments** | **12,884,901,888** |
| Full-packet byte/word interpretations compared | 4 |
| Native first-output comparisons | 51,539,607,552 |
| Matches to first untouched 64-bit source word | **0** |
| Matches to both untouched original packet words | **0** |

A direct C++17 -O3 local run completed, process exit **0**, about **22.37 s** CPU-bound wall time in the final source-equivalent implementation. The program's genuine enumeration path recovered **16/16 independently planted whole two-output packet positives** (two signed/unsigned seed domains × two state orders × four serializer views) using small seed intervals, not leaked seed/state values. Additional seed/packet roundtrip checks passed. The earlier, more verbose independently coded runner also completed 12,884,901,888 assignments with the same zero counts and 16 planted enumerator positives. The original selected ACK2 is not read.

Reproducer: [exact remotely committed, locally compiled and tested C++ source](../agents/agent31/k04_xoro_seed32_exhaustive.cpp). The published Git blob SHA `10d5c6730eaf39c8a3fa46259998f0ea83d04f43` was checked against the local file's `git hash-object`; they match byte-for-byte.

## What this excludes and where to go

**No 32-bit-seeded canonical SplitMix64 → xoroshiro128++ initialization from either two-word order, either unsigned/signed seed mapping, and any of the four packet serializers can produce even the first intact original REQUESTED1 word at generator offset zero.** Thus this entire finite low-entropy startup domain cannot yield the physical K04 coupon *through that first-request continuity premise*. This is a genuinely stronger exhaustive seed exclusion than sampling human-readable date/job seeds.

It does **not** exclude 64-bit or 128-bit seeds, a seed transformed before SplitMix64, intervening initial draws (nonzero generator offset), alternate state mixers, a different printer producer, or the seed-free compatible states already being enumerated by other agents. It also cannot recover K08's author-final phrase. The original acceptance state remains six PASS, K04/K08 MISSING and REC8/1 INCOMPLETE. **Do not mistake the zero first-word hit for a general xoroshiro128++ exclusion or spawn equivalent 32-bit date seed screens.**
