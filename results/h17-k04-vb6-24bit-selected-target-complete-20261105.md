# Exact 24-bit Visual Basic `Rnd` selected-coupon frontier (5 November 2026)

## Distinct producer hypothesis

The historical north printer coupon could have been emitted by a legacy Visual Basic `Rnd` source with an unknown 24-bit internal state. This hypothetical **selected-event-only** producer is separate from older MSVC CRT `rand()` work (32-bit state, different coefficients), and does not assume that an ordinary spool packet shares the exceptional producer.

The documented Visual Basic recurrence is `x_next = (1140671485*x + 12820163) mod 2^24`. It is documented in historical Microsoft KB 231847, mirrored at [BetaArchive](https://www.betaarchive.com/wiki/index.php/Microsoft_KB_Archive/231847). No source record independently identifies Visual Basic as the printer software.

**Full selected-target test:** Enumerated all `2^24 = 16,777,216` possible 24-bit *internal states*, which covers arbitrary integer seeding and all prior draw phases because the multiplier is invertible modulo `2^24`. For each state generated complete 16-byte coupons in nine output views: one byte per `Rnd` output from each of the three state-byte lanes, plus full three-byte-packed outputs in both byte orders and all three byte-alignment phases. Checked both coupon byte orientations.

Each complete coupon is XORed with the **unchanged original K04 route mask** `8556C8CB6140A7F9A5123AC7571BEE1C`, and the resulting 16-byte component is SHA256-checked against the **original K04 commitment** `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. Input acceptance, source and candidate files are unchanged.

## Computation and controls

Original OpenSSL SHA256 C implementation: [`agents/agent4/k04_vb6_selected_target_sft.c`](../agents/agent4/k04_vb6_selected_target_sft.c).

Four nonoverlapping exhaustive state shards:

| Seed-state interval (end exclusive) | Full candidate hash checks | Original matches |
| --- | ---: | ---: |
| 0..4,194,304 | 75,497,472 | 0 |
| 4,194,304..8,388,608 | 75,497,472 | 0 |
| 8,388,608..12,582,912 | 75,497,472 | 0 |
| 12,582,912..16,777,216 | 75,497,472 | 0 |
| **Total** | **301,989,888** | **0** |

A planted synthetic **complete 16-byte** coupon with true internal state `0x123456`, little-endian 24-bit packing, byte phase two, and reversed coupon orientation was recovered at exactly the planted state/variant by the same program when using the synthetic target digest. This validates complete SHA256 matching, masking, phase enumeration and target selection; the original run always uses the unmodified original commitment.

## Original-source crosscheck and limitations

An independent first ordinary printer packet full-payload test scanned all 24-bit possible first states compatible with each output byte view (including reversed coupons). Six whole-packet byte-extraction source cases were negative. The four three-byte-aligned source views were also negative; the additional six packed arbitrary byte-offset/orientation views are negative. Fifteen synthetic seed+byte-lane tests and six packed arbitrary-offset positive controls passed. Source-only reproducer: [`agents/agent4/k04_vb6_rnd_source_sft.c`](../agents/agent4/k04_vb6_rnd_source_sft.c).

This exhaustively excludes the **nine specified 24-bit Visual Basic stream packing conventions**, under either coupon orientation and original K04 reducer, even if the selected coupon alone used this producer. It does **not** exclude other byte transforms, multiple generators, secret-dependent emission, or a physical copy-stage replacement. The producer is hypothetical and fails independent ordinary-source packet controls.

**Recovered K04 bits: 0/128. Recovered K08 terminal words: 0. Original verifier remains six individually PASS and combined INCOMPLETE.**
