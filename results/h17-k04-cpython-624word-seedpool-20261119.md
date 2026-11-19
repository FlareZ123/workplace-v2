# K04 CPython 624-word seed-pool screen

**Agent 50 | 19 November 2026 | Source-pinned exploratory candidate test; no K04 recovery.**

## Question

The archive contains two previously identified 624-word source pools. Earlier work tested these words as a direct MT19937 state or as a contiguous output stream. This experiment tests a distinct construction: use each pool as the 624-word integer key array for CPython's standard `random.Random(int)` / MT19937 `init_by_array` initializer, then derive the missing coupon at its natural spool-row position.

This is an archive-derived, noncausal hypothesis: the seed pool includes intact spool rows that occur after the missing row. It is tested as a deterministic reconstruction mechanism, not asserted as the historical printer's live generator.

## Source pools and fixed selector

The source-pinned inputs are the 132 intact 16-byte spool payloads (selected row 129 excluded), all 88 original TRP2 control words, and one of two pairs of four-word source blocks:

- **P+R+K02+K07:** 528 spool words + 88 recorder words + four K02 prehash words + four K07 prehash words = 624.
- **P+R+K01+K06:** 528 spool words + 88 recorder words + four accepted K01 words + four accepted K06 words = 624.

The selected event remains the exact 18:02Z ACK/RECOVER attempt 2 for `PS-261003-0417`, at zero-based spool row **129**. Its four-word output position is therefore **516**. The selected copied payload is asserted as a selector and excluded from every seed pool.

The script pins the original spool and recorder SHA-256 values, validates the selected row, checks the K01/K03/K05/K06 accepted components against their original slot commitments, and verifies that the K02/K07 prehash blocks produce their accepted components. The original route mask and full K04 commitment are read unchanged from the original acceptance/routing files.

## Complete finite construction

For each 624-word pool, enumerate:

- all 24 orders of the four source groups;
- eight printer views (word byte order, packet-row direction, and within-packet word direction);
- eight recorder views (four source record orders: physical, reverse, timestamp, and node/event/latch/sequence; each with both word byte orders);
- four views for each 16-byte K01/K06 or K02/K07 block (both word byte orders and forward/reverse word order).

This is **24 × 8 × 8 × 4 × 4 = 24,576 seed arrays per pool**. Every integer retains all 624 key words. For each seed, CPython emits 520 32-bit values; the candidate coupon is the four consecutive outputs at positions **516–519**.

Each coupon is serialized in eight ways: tempered or untempered MT words, little- or big-endian bytes per word, and forward or reverse word order. The unchanged K04 route mask is XORed with the complete 16-byte coupon; SHA-256 of the resulting 16-byte component is compared with the original full K04 commitment.

## Executed result

| Seed pool | 624-word layouts | Complete K04 candidate checks | Commitment hits |
|---|---:|---:|---:|
| P+R+K02+K07 | 24,576 | 196,608 | **0** |
| P+R+K01+K06 | 24,576 | 196,608 | **0** |
| **Total** | **49,152** | **393,216** | **0** |

All 49,152 seeds retained a 624-word integer key. The synthetic positive control constructed a coupon from a known 624-word seed at the same output offset; the identical serializer and mask/hash path recovered that planted coupon, while a one-byte mutation failed. The original-data run completed locally in approximately eight seconds.

**No original K04 candidate passed.** No original source, route, acceptance commitment, verifier, or canonical candidate was modified.

## Interpretation and limits

This excludes only the tested CPython integer-seed-array construction over these two 624-word source pools, the enumerated source views, output offset 516, and eight output serializations. It does not exclude another source pool, seed derivation, PRNG, stage/offset rule, or a genuine physical coupon. The archive-derived seed is noncausal and remains a speculative reconstruction model; a commitment hit, had one occurred, would still require separate historical-authenticity assessment.

The result adds a distinct test beyond the prior 624-word-as-state and contiguous-stream studies, but it yields **zero authenticated K04 bits** and no K08 words. Do not expand this same seed-pool family without a new source-dependent reason. Continue toward a selected-event whole-object discriminator for K04 and an author-final wording carrier for K08.

**Reproducer:** [`agents/agent50/k04_cpython_624word_seedpool_sft.py`](../agents/agent50/k04_cpython_624word_seedpool_sft.py).
