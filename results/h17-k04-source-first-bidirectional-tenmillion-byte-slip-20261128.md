# K04 — source-compatible state, 10 million forward + reverse native stages, four serializers × sixteen byte slips

**Agent 37 · 28 November 2026 · completed authentic original-target private computation; no recovered K04**

## Actual target-reaching experiment

Rather than trying another arbitrary packet donor, Agent 37 first obtained **one complete 128-bit xoroshiro128++ 1.0 initial state that exactly reproduces both intact 64-bit words of original PS-261003-0417 / ATTEMPT=1 / REQUESTED / RECOVER**, under the declared **little-endian, two-word AB** view. This full state was found inside an exact, complete P12/P16 parent partition, by fitting the first packet only and withholding the disputed selected ACK2. It is an unconstrained nonlinear producer hypothesis, **not evidence that this PRNG drove the historical printer**. Its state words were stored only in a local mode-0600 out-of-repository receipt.

The original state was replayed against the whole independently retained REQUESTED1 16-byte packet before reuse. The unchanged original K04 route mask was XORed onto **every complete 16-byte hypothesized coupon**. Each resultant **whole 16-byte component** was SHA256-hashed and compared to the **unchanged complete original K04 slot commitment**. The later original REQUESTED3 retry and copied selected ACK2 were **not used as admission filters**.

From that source-compatible state, a separate local C++17/OpenSSL streaming reducer scanned:
- **Forward** native output starts 2..10,000,001 inclusive. Each start uses four chronological consecutive 64-bit xoroshiro128++ outputs to form two 16-byte packets in each of the **four** BE/LE × AB/BA serialization views; every **0..15** starting byte offset in the resulting 32-byte view is a complete 16-byte candidate. The local C++ run was split into **100,000 + 9,900,000** disjoint start ranges.
- **Reverse** native starts -10,000,000..-1 inclusive. The exact invertible xoroshiro128++ transition is reversed from the original source-compatible initial state; each reverse start is again checked in all **four** serialization views and all **sixteen** complete byte-slip offsets, allowing a coupon to precede the first retained REQUESTED1 packet.
- Original target and candidate bytes were never printed, stored in GitHub, or dispatched to public CI. Every actual commitment match count is aggregate-only; any recovered component requires private escrow and official original verifier acceptance before publication.

## Completed original result

| Source-compatible conditional state | Native start positions | Standard packet views | 16-byte offsets per view | Complete K04 SHA256 assignment checks | Original K04 commitment hits |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forward stages +2..+10,000,001 | 10,000,000 | 4 | 16 | **640,000,000** | **0** |
| Reverse stages -10,000,000..-1 | 10,000,000 | 4 | 16 | **640,000,000** | **0** |
| **Total** | **20,000,000** | | | **1,280,000,000** | **0** |

These are **assignment checks**, not guaranteed unique 16-byte components, because adjacent native starts and byte-slip windows may overlap. The negative covers only this exact source-compatible generator state, stage windows, output-word layout, and byte-slip family. Other original firstpacket-compatible states remain possible until all P12 parents/UNKNOWN branches are closed; resetting the producer between events or using a different algorithm remains outside this exclusion.

The local native C++17/OpenSSL run produced these exact aggregate-only receipts:
- Forward short shard: 6,400,000 complete checks, original hits 0.
- Forward long shard: 633,600,000 complete checks, original hits 0; 195.06 seconds of process CPU.
- Reverse full run: 640,000,000 complete checks, original hits 0; 194.60 seconds of process CPU.

An independent prior Python source-first reducer for the same state, one declared serializer and 65,536 whole-packet gaps × 16 byte slips, also returned 0/1,048,576 original hits and zero later whole-word/full-packet replays. The new C++ experiment is a strict offset/layout extension for this state, not a new source of original coupon bytes.

## Independent copied-ACK consistency diagnostic (post-fit, not a source constraint)

The surviving selected ACK2 spool payload is expressly **not media-authenticated**, and was never used to fit the initial generator state or select its P12/P16 branch. After the original 1.28 billion full K04 commitment comparisons, a separate, less stringent copied-fragment consistency screen compared each **pre-mask 16-byte generated coupon** to that copied ACK2 byte sequence. It used the identical 20 million bidirectional native starts, four serializer views and 16 byte slips. For each complete hypothetical coupon it computed (a) the number of bytes identical in the same positions and (b) the full 128-bit Hamming bit distance. These are comparison diagnostics, **not** additional authenticated K04 component checks.

| Hypothesized source-compatible stream | Compared full 16-byte assignments | Maximum exactly matching byte positions with untrusted ACK2 copy | Smallest 128-bit Hamming distance | Assignments matching at least 8 of 16 copied bytes |
| --- | ---: | ---: | ---: | ---: |
| Forward 10 million native starts | 640,000,000 | **5** | **32 bits** | **0** |
| Reverse 10 million native starts | 640,000,000 | **5** | **29 bits** | **0** |
| Combined | **1,280,000,000** | **5** | **29 bits** | **0** |

In particular no generated coupon in those windows shares even **six** exact positions with the retained selected ACK2 copy. Thus any hypothesized coupon from this *particular* recovered source-compatible state and enumerated output family would require at least **eleven byte positions** (and at least 29 bits) to differ from the copied ACK2 buffer. This bounds a conditional near-copy-damage story; it is **not** proof of any actual corruption count because the source neither authenticates the PRNG nor puts an upper bound on how badly that buffer was reconstructed.

The separate, private C++ source diagnostic pins the original spool SHA256, independently replays the full 16-byte REQUESTED1 source against the private state, then scores the unique original ACK2 copied line without printing its bytes. A source-free planted comparison control used a coupon at forward/reverse stage 317 in an alternate packet serializer at byte slip seven and changed exactly **three byte positions / four bits**. Both modes recovered the stipulated best bit distance and at least 13 equal bytes. The historical result above requires **no acceptance-target feedback** during comparison. It makes a stronger discrimination between simple copied-byte proximity and random generator coincidence without claiming an original K04 hit.

## Reproducibility and controls

The [shared C++17/OpenSSL source-ready state continuation tool](../agents/agent15/k04_xoropp_source_state_longstream_local.cpp) was initially supplied by Agent 15 and extended in [Agent 37's reverse-byte-slip commit](https://github.com/FlareZ123/workplace-v2/commit/ce62f96316044667911495db89c74463277b8c2b) so `--byte-slips` applies to **both forward and reverse** stages. Its packed-packet / SHA test is equivalent to the independent local C++ reducers used for the original measurements; the actual historical runs used the private local independently compiled equivalents and retained only aggregate logs.

Compile source-independent controls locally (never run original source in public CI):

```sh
c++ -O3 -std=c++17 -Wall -Wextra agents/agent15/k04_xoropp_source_state_longstream_local.cpp -lcrypto -o /tmp/h17-k04-longstream
/tmp/h17-k04-longstream --synthetic
```

For a researcher already possessing a **private** original firstpacket-compatible two-word state and permitted original non-PDF source files in a local, restricted resources directory, the equivalent target-facing invocation is:

```sh
env -u CI -u GITHUB_ACTIONS /tmp/h17-k04-longstream \
  --resources-root /PRIVATE/approved-resources \
  --state-file /PRIVATE/0600-state-words.txt \
  --source-view little/ab \
  --forward-pairs 10000000 --reverse-pairs 10000000 \
  --byte-slips --hit-escrow /PRIVATE/0700-dir/verified0600.txt
```

Do not copy an original state, source token, target-bearing coupon, private hit file, or prohibited PDF bytes into GitHub or an external runner. The consumer itself asserts complete REQUESTED1 replay, original source SHA pins and private-escrow properties. The local independent source-reader pinned:
- spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`;
- routing SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`;
- acceptance SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

**Positive controls:** The forward synthetic case planted an independently hashed complete masked coupon at native stage +413, alternate big/BA packet serialization, unaligned byte offset 7; the identical candidate reduction found it. The reverse source-free case independently planted stage -413, big/AB, offset 9; the exact inverse transition and full 16-byte acceptance found it. The upgraded shared C++ tool also asserts a reverse stage -73 / offset 9 alternate-serializer positive in `--synthetic`.

## Recovery meaning and next discriminator

This is an exceptionally wide **conditional** complete-coupon acceptance test for a *truly source-compatible* firstpacket generator state. It rejects both ten-million-start contiguous output families in all four standard packet views and 16 offsets for that state, not a physically authenticated copier reconstruction, not the generator class as a whole, and not the source archive's original K04 slot. Model-complete firstpacket state enumeration is an active separate step via the [exact adaptive P16/P20 solver](../agents/agent37/k04_p16_p20_adaptive_source_local.py) and [private replayable P12 parent receipts](../agents/agent37/k04_p16_parent_receipt_local.py).

K01/K02/K03/K05/K06/K07 remain original verifier PASS; **K04 and K08 remain MISSING; REC8/1 combined INCOMPLETE**. No commitment-hitting component exists in this scan. Historical source paths absent from the export and author-final desk wording are not invented.
