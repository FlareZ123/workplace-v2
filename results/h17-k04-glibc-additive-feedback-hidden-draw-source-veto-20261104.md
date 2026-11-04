# K04: glibc random() additive-feedback, exact bounded hidden-draw source veto

**Agent 4 | 4 November 2026, 19:40–19:46 UTC.** Source-only, read-only producer test; **32/32 complete variants rejected without consulting the disputed selected payload or either missing slot commitment**. It neither recovers K04 nor settles other PRNGs.

## Why this is an additional producer architecture

The preserved H-17 spool contains exactly 128 ordinary five-minute ACK jobs, 0300..0427, each with an opaque 16-byte payload. Previous MT19937, xorshift, PCG, .NET subtractive, CRC and affine models did not test GNU glibc's **31-word additive-feedback generator** with its characteristic lags 31/3, nor its `initstate` variants with lags 7/3, 15/1, 63/1. A Linux printer-side or import-side `random()` or `rand()` wrapper could emit the low or high 8/16 bits of one generator result per coupon byte/halfword, with extra random draws between jobs. This is a **hypothesis**; the original source gives no printer firmware provenance or POSIX generator claim.

The genuine <https://github.com/bminor/glibc/blob/master/stdlib/random_r.c> implementation defines output `o[t] = state[t] >> 1` and additive feedback `state[t] = state[t-degree] + state[t-separation] mod 2^32`. Therefore any fixed contiguous 8-bit or 16-bit slice of its outputs necessarily satisfies

`o[t] = o[t-degree] + o[t-separation] + c (mod 2^width)`, where `c∈{0,1}`.

A **single** violation at an index where all three values are visible disproves that complete chronology. This is a necessary test, so it cannot reject a true generator by ignoring hidden low-bit carry.

## Exhaustive bounded source test

Exclude all five late packets entirely, including the selected copied K04 row. Read only the first **eight intact ordinary packets** from jobs 0300..0307. Consider four independently fixed, physically conventional byte layouts: raw 16 bytes, full reverse, reverse four 4-byte words, and byte-reverse within each 4-byte word. For each:

- 8-bit extraction: 16 consecutive output bytes per packet, hidden gap of **0..16 generator outputs** between successive packets, full recursive enumeration of all geometrically reachable starts.
- 16-bit extraction: eight consecutive output halfwords per packet, endian BE/LE and forward/reverse word order. Hidden gap **0..8 outputs** for lags 7, 15 and 31; **0..6 outputs** for lag63.
- Direct 32-bit packing: four little- or big-endian words per packet, in forward/reverse word order. The first eight packets already contain **12 or 14 of 32 values with the top bit set**, impossible for unchanged glibc `random()` outputs, which are 31-bit.

There are **4 orientations × 4 recurrence types × 2 slice widths = 32 complete source-sieve variants**, in addition to four 32-bit exclusion orientations.

| Source slice width | Table degree / separation | Maximum hidden draws between 16-byte packets | Result | Max explored recursive nodes per orientation |
| --- | --- | ---: | --- | ---: |
| 8-bit | 7/3, 15/1 | 16 | All reject inside first packet | 1 |
| 8-bit | 31/3 | 16 | All reject by second packet | 18 |
| 8-bit | 63/1 | 16 | All reject by fifth packet | 2,636 |
| 16-bit | 7/3, 15/1 | 8 | All reject by second packet | 1, 10 |
| 16-bit | 31/3 | 8 | All reject by fifth packet | 505 |
| 16-bit | 63/1 | 6 | All reject within eight packets | 95,474 |

Every 8/16-bit variant completed its entire bounded search without a node cap, and **zero** original source-compatible eight-packet streams survived.

**Important coverage limit:** With 16-bit packet units and lag63, extending the permitted gap to 8 outputs produces a seemingly compatible alignment `[7,0,0,0,0,0,7]` across the first eight packets, **but it witnesses zero complete glibc recurrence triples**. It is purely a geometry that avoids all constraints and cannot be promoted as an actual source fit. For that reason the reported finite negative explicitly uses the tighter 0..6 bound. Interleaved byte emission, per-job reseeding, multiple streams, larger gaps, and other PRNGs remain open.

## Genuine controls, provenance and decision

[The source-pinned SFT](../agents/agent4/k04_glibc_additive_gap_sft.py) calls the actual installed GNU libc `initstate(seed=42)` with state buffers of **32, 64, 128, 256 bytes** to instantiate all four degree/separation variants. For each, it checks **1,000 original libc outputs** against the full 31-bit recurrence and both truncated widths, constructs eight synthetic 16-byte packets with seven nonzero/zero mixed hidden gaps `(2,0,3,1,4,2,1)`, then proves that the same backtracking search **recovers their exact genuine hidden-gap layout**. All eight 8-/16-bit synthetic positives passed. The original spool is asserted by SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

This source-only falsifier differs from fitting a target commitment to speculative printer repairs: the historical 18:02 K04 data, K04 SHA and K08 HMAC never enter the sieve. It closes a bounded native POSIX additive-feedback producer possibility without adding a recovered coupon bit or caption word. Future work should seek an **authentic producer-stage or selected-media witness**; merely allowing unbounded gaps in this model produces uninformative source compatibility.
