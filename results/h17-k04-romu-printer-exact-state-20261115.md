# H-17 K04: exact Romu printer-state recovery, original-source and target result (15 Nov 2026)

**Agent41 | Original K04 whole-commitment matches: zero.** Six other REC8/1 slots remain accepted; K04/K08 unresolved, combined INCOMPLETE.

## Distinct candidate-producing hypothesis

The surviving printer log has 128 ordinary five-minute ACK rows, then the selected PS-261003-0417 REQUESTED1 (18:01), damaged-copy ACK2 (18:02), and intact REQUESTED3 (18:03). Model its opaque 16-byte fields as native outputs of the published [Romu rotate-multiply PRNG family](https://www.romu-random.org/), with byte/word endian and fixed word-order alternatives. This is an exploratory producer assumption, **not an attested historical printer algorithm**. The copied selected ACK2 bytes are withheld from every state reconstruction.

Original input printer SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Original K04 route mask: `8556C8CB6140A7F9A5123AC7571BEE1C`. Original K04 SHA256 commitment: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Exact source-only next-output screens

| Model | Complete producer-state recovery | Genuine original source predictions | Exact matches |
| --- | --- | ---: | ---: |
| RomuDuoJr 64-bit native outputs | two consecutive 64-bit outputs | 3,968 next-u64 | 0 |
| RomuDuo 64-bit | two outputs | 3,968 next-u64 | 0 |
| RomuTrio 64-bit | three outputs | 3,904 next-u64 | 0 |
| RomuMono 32-bit native output | two consecutive outputs determine 64-bit state | 8,064 next-u32 | 0 |
| RomuTrio32 32-bit | three outputs determine 96-bit state | 8,000 next-u32 | 0 |
| RomuMono32 16-bit | first output plus all 65,536 hidden low-state values | 528 whole 16-byte packets | 0 |

The ordinary rows were tested both as a chronological stream and in CLASS/DEST partitions under the documented serializers. All source SHA and planted-state/heldout-output controls passed. RomuTrio32 separately failed the internal fourth output in all 2,048 packet view/group tests. RomuMono32 retained 518 initial two-word residue matches but **zero complete eight-word original packets**.

## Complete K04 physical-coupon candidate reconstruction

| Hypothesized selected producer stage | Complete K04 components tested | Authentic K04 whole SHA256 hits | Intact 18:03 whole-packet predictions |
| --- | ---: | ---: | ---: |
| Invert 18:01 REQUESTED1 as native RomuDuo/Jr, immediate next two u64 | 8 | 0 | 0/8 |
| Same 18:01 source state, unknown draws; all 131,071 two-u64 windows per serializer | 1,048,568 | 0 | 0 |
| Invert 18:01 as RomuQuad32, full 2^32 initial-state-domain per four serializer views; next four u32 | 6 | 0 | 0/6 |
| Same six RomuQuad32 states, 131,072 four-u32 candidate windows per state | 786,432 | 0 | 0 |
| Independently invert *later* 18:03 REQUESTED3 as RomuQuad32 and rewind four native u32 | 2 | 0 | 0/2 for previous 18:01 |
| Two reverse-recovered RomuQuad32 states, 131,072 earlier four-u32 windows each | 262,144 | 0 | N/A |

The RomuQuad32 forward inversion is **algebraically complete** under its source model: four observed outputs provide three equations in three initially hidden 32-bit words, leaving exactly one 32-bit state variable for exhaustive enumeration. With official odd multiplier `3323815723`, every possible one-word residue (2^32) is examined under each of four whole-packet serializers. Six complete initial states survive. For reverse recovery, the inverse multiplier `0x33621f83` makes the 128-bit recurrence exactly reversible. Two complete states survive the intact later source; neither yields K04.

**Execution controls:** 1,000 planted whole-state forward inversions; 1,000 planted 64-step forward/backward generator round trips; synthetic genuine Romu family output controls and mutation negatives. No original acceptance data, official verifier, source archive or canonical candidate was modified.

## Reproducers and uncertainty

- [64-bit Romu ordinary source](../agents/agent41/k04_romu_original_source_sft.py), [RomuMono 64/32](../agents/agent41/k04_romu_mono_source_sft.py), [native32 Trio/Mono](../agents/agent41/k04_romu_native32_source_sft.py)
- [Selected same-job Duo/Jr immediate](../agents/agent41/k04_romu_selected_retry_sft.py), [Duo/Jr hidden draws](../agents/agent41/k04_romu_variable_gap_sft.py)
- [Quad32 forward complete inversion + hidden draws](../agents/agent41/k04_romuquad32_fullstate_sft.cpp), [Quad32 reverse exact inversion + hidden draws](../agents/agent41/k04_romuquad32_backward_sft.cpp)

These are **finite producer exclusions**. They do not establish actual source/physical selected bytes and do not exclude a different producer, session reset, asymmetric printer buffer transform, unknown serializer or wording-source dependency. No target value or new K04 bit has been authenticated. The strongest incremental method is complete **target-bearing state inversion** from both genuine same-job neighboring records, rather than a blind byte edit. Future work should change the causal producer model or source relation, rather than re-enumerate these identical Romu laws.
