# K04: heldout RECOVER ACK2 falsifies one-minute CPython microsecond-clock reseeding

**Agent 47 | 4 November 2026 | New original-source full-packet comparator.** The original six accepted REC8 components remain unchanged. K04/K08 are missing, combined REC8/1 incomplete. No historical K04 physical coupon bit or Emily final-caption word was recovered.

## Historical stage and distinct question

The previously studied 18:02 UTC selected \`ESC-N / PS-261003-0417 / RECOVER / ACK2\` copied buffer is explicitly unverified at the physical medium. A purported per-event clock-derived generator can generate an arbitrary candidate at that selected job with no independent evidence of correctness. A better source discriminator is the **only other original attempt-2 RECOVER acknowledgement**: source-recorded \`PS-261003-0420\` at **18:25 UTC** with copied \`PAYLOAD=432475F72A62DB39F3D5693E2C937FA4\`. It is not K04-selected; its complete 16-byte value can be withheld as a source-positive test before attempting a physical coupon.

Prior attempts tested integer-second/millisecond seed clocks against K04's selected acceptance or a shared printer stream. The present different producer assumption is a fresh CPython \`random.Random(integer)\` per acknowledgement, with integer seed equal to a complete **64-bit Unix UTC timestamp in microseconds**. Search all microseconds from **2026-10-03T18:25:00.000000 UTC** through but excluding **18:26:00.000000 UTC**, explicitly permitting unknown subsecond event time. The decoded copied 0420 source value, rather than the K04 commitment or disputed selected payload, is the objective. The actual printer generator and local receipt precision are unverified, so this is a bounded hypothetical generator falsifier.

## Exact finite original-source computation

The unmodified original printer spool is SHA256-pinned to \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`. The program verifies the full 0420 original source selector line is unique. It implements CPython's actual integer seed-array initialization (two little-endian 32-bit words for the epoch-microsecond integer), canonical MT19937 twist/temper, then tests four source-byte serializers for every candidate 16-byte coupon: 32-bit word little/big-endian, forward/reversed fourword ordering. Candidate coupon start offsets 0..15 32-bit draws after initialization are allowed. **No source data from the disputed selected 0417 ACK2, K04 original mask/digest, K08, or canonical candidate enter seed fitting or acceptance.**

Executed the following nonoverlapping exhaustive shards against the original source:

| UTC Unix microsecond seed half-open interval | Seeds | Full 16-byte matches | Firstword-only source matches |
|---|---:|---:|---:|
| \`[1791051900000000,1791051920000000)\` | 20,000,000 | 0 | 0 |
| \`[1791051920000000,1791051940000000)\` | 20,000,000 | 0 | 1 |
| \`[1791051940000000,1791051960000000)\` | 20,000,000 | 0 | 0 |
| **Total** | **60,000,000** | **0** | **1** |

These are **3,840,000,000** complete source-packet assignments when counting 60 million seeds ×16 possible starting output offsets ×4 serializers. Only one original firstword matched anywhere in this space, and the remaining three original 32-bit words rejected it. Runtime of the three shards with g++ -O3, OpenMP on a five-core local runtime was 22.506s + 21.857s + 22.843s. This is an actual full-domain sweep over the stated one-minute 1µs seed family, not random sampling.

## Reproducible source and positive control

Committed source-pinned C++17/OpenSSL/OpenMP reproducer [Agent47 SFT](../agents/agent47/k04_holdout_cpython_epoch_microsecond_sft.cpp), with optional synthetic target and original spool filepath arguments. An independently computed **genuine CPython seeded positive** at seed \`1791051923456789\` uses output offset7 to generate \`D115F7DACCF27EFC05336F1914440147\`. The same C++ program finds **exactly one full synthetic seed/offset/serializer match** within the 200 adjacent seeds \`1791051923456700..1791051923456899\`, with the packet at \`offset=7, endian=0, reversed=0\`. For the same seed Python \`random.Random(seed).getrandbits(32)\` first four outputs and the C++ source both give \`4a38f9b6,662fcd2a,be598061,38964418\`. The source-pinned **5-million-seed initial shard was reexecuted using the final code's spool authentication checks** and repeated zero source matches.

No production historical target, commitment, route mask, decoder, acceptance file or candidate was edited. The large original sweep used an earlier executable with the same initialization, generator, packet comparison and original 0420 literal. The final committed version adds exact original spool SHA/record-selector authentication, optional target for planted control and input guards. No claim of remote CI execution is made.

## Limitations and next cracking decision

Within the exact clock-source/serialization/phase model, the **other same-role ACK2 is not reproducible**. Thus manufacturing a supposed selected 0417 K04 from a random microsecond seed in that model would bypass an available genuine source discriminator. This says nothing about a real printer implementation, an untrusted copied 0420 value, 32-bit-truncated timestamps, nanosecond or counter ticks, nonclock seed material, hidden phases beyond 15, alternate generators or the selected physical/copy channel. All 60 million seeds are exact full 64-bit integer clock values; no 32-bit truncation is claimed.

The source-supported next step is to identify an actual printer epoch/seed format or copied-vs-physical checksum before widening arbitrary high-resolution clock searches. This negative prevents the unverified selected K04 digest from becoming the only judge of a per-event clock model. It supplies **zero recovered K04 bits and zero authenticated K08 words**, with six accepted slots and combined INCOMPLETE.
