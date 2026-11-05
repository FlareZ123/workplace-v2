# K04: unindexed four-field MT19937 printer fingerprint and selected-stage donor gap

**Agent 9 | 5 November 2026 UTC. Original K04 remains unresolved.** A direct source-only four-word numerical experiment locates **25 exact full-32-bit MT19937 twist relations** in the original intact printer data **before any MT stage indices are supplied**. Every relation also satisfies the older conditional p951 stage map, but the 18:02 UTC selected 0417 attempt-2 ACK has no complete backwards triple among directly preserved outputs. This strengthens one publisher hypothesis without recovering a selected coupon bit. The original six REC8 slots still PASS, K04/K08 MISSING, combined INCOMPLETE.

## Why this is a separate source test

Earlier [Agent49 p951 symbolic source basis](../agents/agent49/k04_p951_symbolic_basis.py), [Agent4 foreign four-field bridge](h17-k04-rc17b-exact-fourword-twist-crosscarrier.md), and [Agent32 future 227-pair donor analysis](h17-k04-p951-227-pair-target-window.md) prescribe native MT positions, or require external cross-record values. Here **the numerical relation is discovered globally within the unselected printer packets without using any absolute native stage or target-side value**. The later check against the established p951 array is a separate, explicitly retrospective confirmation rather than independent stage discovery.

This test is useful because a source-fit under a high-dimensional linear quotient can fail to distinguish a true common 32-bit MT emitter from an opportunistic label-to-state assignment. Direct discovery of exact, chronological four-value equations gives a different discriminator. It is still not proof of physical producer software or that the missing original was emitted by this exact generator.

## Full-source, target-blind construction

Original printer source SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Parse all 133 original 16-byte printer packets; withhold **entire** row129, whose source metadata identifies `PS-261003-0417 / attempt2 / ACK / RECOVER`. This gives 132 intact 16-byte packets or 528 source words. The copied 129th buffer, route mask, K04 and K08 commitments, and official candidate are absent from every test input. Nothing is written to the original resources.

For each of eight source presentations (little/big 32-bit endian, forward/reverse fourword packet order, raw/native-untempered) enumerate native word positions i,j=i+1 **inside a single intact packet**, and source positions k,l in later chronological packets with 32<=l-k<=250 flattened observed words. Check the complete numerical identity:

```text
N[l] = N[k] XOR ( ( ((N[i] & 80000000) | (N[j] & 7FFFFFFF)) >> 1 )
                XOR (9908B0DF if N[j] bit0 else 00000000) )
```

All quantities are 32-bit words. The test uses a hash index of right-side source-pair XORs; there is **no K04 hash or fitted MT stage parameter** in the search. The observed-word gap 32..250 is a broad discovery bound, not the physical MT lag of 227; only original chronology and source-packet boundaries restrict matching.

| Source interpretation | Exact chronology-compatible source relations |
| --- | ---: |
| Little endian, untampered output bits (no inverse MT temper), forward packets | 0 |
| **Little endian, inverse-tempered MT native words, forward packets** | **25** |
| Little endian, raw bits, reversed fourword order | 0 |
| Little endian, inverse-tempered, reversed fourword order | 23 |
| Four big-endian layouts (raw/inverse-tempered, forward/reverse words) | 0 |

This search intentionally permits the reverse-word orientation as a control, and therefore some of the same native twist ancestry may be encountered under different order conventions. Counts are individual source relations, not an independent-hypothesis count and not candidate coupons.

One exact witness, forward little-endian, extracted at flat preserved-word positions **0,1,215,332** (source rows 0,0,53,83):

```text
X[0] = 865565A6
X[1] = EE2ADF82
X[215] = E522D4DE
X[332] = 9237BB1F

MT_twist_mix(X[0], X[1]) = 77156FC1
X[215] XOR X[332]       = 77156FC1   (exact 32 of 32 bits)
```

The **25** forward little-endian source matches, computed with no stage positions, each independently match Agent49's already available original stage map with exact stage gaps **397 and 624**. In a genuine synthetic Python MT stream sampled at exactly those original packet positions, with its selected row withheld, the same stage-free search reports exactly **25** relations. All input temper/untemper inverses also pass 100 random 32-bit roundtrips.

## Placebos and inference limits

Retain the entire original set of 528 4-byte source values and each original packet's membership, but independently permute the four word orders within each packet for **128 seeded shuffles**. Under the fixed previously proposed p951 index array, shuffle samples retain **0–3 exact stage-aligned recurrences**, mean **0.4296875**, compared with **25/25** originals. If one counts the unindexed relation only, many shuffled permutations still match because MT's twist law uses just one bit of the first operand; the report deliberately does **not** present those as absent. Sixteen separate independent-random 132-packet controls have zero unindexed matches under the tested 32..250 observed-word-gap bound. The positive is therefore a concrete **source-structure fingerprint**, although the p951 comparison remains retrospective.

## Direct selected-coupon non-observability

Under this now strongly source-compatible **conditional** stage map, row129 would occupy native stages **951..954**. The backward MT equation for each unknown selected native word at stage q needs three source native words q-624, q-623, q-227. The exact original-surviving output-position availability is:

| Unknown selected native stage q | Required earlier native positions | Directly observed among the three |
| ---: | --- | ---: |
| 951 | 327, 328, 724 | **1** (327) |
| 952 | 328, 329, 725 | **0** |
| 953 | 329, 330, 726 | **0** |
| 954 | 330, 331, 727 | **0** |

Thus these 25 exact source relations validate parts of a generator architecture **without furnishing a complete target-causal reverse relation for any selected word**. The stronger original-source GF(2) quotient independently reports all 128 selected bits free at stage951 under this same model. A target-reaching method requires independent authentic future/native donors at conditional stages around 1347..1351 and1574..1578, a source-recoverable initializer, or another original physical coupon representation. The stage-free four-value fingerprint itself does not supply those inputs.

## Reproducer, provenance and next step

[Single-file source-only SFT](../agents/agent9/k04_mt_unindexed_twist_source_sft.py) runs with Python standard library in the repository, asserts the original SHA256, genuine seeded and permutation controls, and all eight exact counts. It reads Agent49's prior stage list *only after* discovering the original native relations. The original ACK2 bytes, mask and acceptance values are never read or modified.

**Next directed crack:** use the 25 source-discovered exact fullword relations as constraints on a newly justified *source-to-native-index mapping*, preferably with an independently selected output carrier that touches q=951..954 or the true paper-copy boundary. Another unrestricted sweep over MT seeds, stages or K04 byte faults without a source-selected donor is unlikely to resolve the 128 free target bits.
