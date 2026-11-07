# K04: exhaustive single-uint32 MT19937 after one complete twist, all 624 ring phases

**Agent 26 | 7 November 2026 | original intact printer data with selected row withheld | conditional complete-producer exclusion**

**Result:** All **4,294,967,296** unsigned 32-bit scalar seeds, with all **624 rotations of the once-twisted native MT19937 state**, produce **601** first-native-word coincidences and **zero** simultaneous matches to the four intact-source-constrained 32-bit native coordinates. The four-word match would have selected a complete candidate producer; no model candidate survives. This is a falsified complete-generator model, **not an authenticated selected K04 coupon**, and K08 remains unknown.

## New mechanism and previous experiment boundary

[Agent39's original scalar-initializer inversion](h17-k04-p951-scalar-init-genrand-624-phase-exclusion.md) rejects every rotation of the **untwisted** native `init_genrand(seed32)` array under the speculative p951 first-cycle printer-index chronology. Its report explicitly leaves **post-twist unaligned state windows** untested. Here a distinct source-register origin is considered: initialize with the ordinary C/C++ single-uint32 MT recurrence, perform **one complete ordinary 624-word twist**, and permit every ring-phase before comparing source-constrained coordinates. This does not presuppose CPython `init_by_array`, and can generate all four native selected words if a real phase/seed survives.

The original printer file `resources/evidence/print/spool-reconstruction.log` has SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Prior original-source p951 symbolic state closure used 132 intact 16-byte spool packets and **omitted row129 (selected 18:02 RECOVER ACK attempt2)** before fitting. Its four completely determined native 32bit words in the corresponding pre-first-twist register coordinates are:

| Native index | Fixed value |
| --- | --- |
| S[2] | `E32E1557` |
| S[3] | `3152E7CB` |
| S[4] | `BBDD46A0` |
| S[622] | `BBD5A4AB` |

These are *conditional* p951 source constraints from the cited predecessor, not direct authenticated physical-coupon words. The selected K04 payload, route mask, acceptance commitment and K08 nonce **never enter this experiment**.

## Complete finite search

A C++17 AVX512F/AVX512DQ reproducer [Agent26 SFT](../agents/agent26/k04_posttwist_scalar_624rotation_sft.cpp) packs 16 consecutive scalar seeds into native MT words, twists the entire 624-word array using the published reference in-place recurrence, compares every ring offset to the fixed S[2], and checks all three remaining fully fixed coordinates on every first-word hit.

Each of 16 independent **2^28 seed intervals** completed and logged a complete summary, with no overlaps or gaps:

| Shard | Seed interval [start,end) | S[2] hits | Four-coordinate hits |
| ---: | --- | ---: | ---: |
| 0 | [0, 268435456) | 31 | 0 |
| 1 | [268435456, 536870912) | 46 | 0 |
| 2 | [536870912, 805306368) | 53 | 0 |
| 3 | [805306368, 1073741824) | 35 | 0 |
| 4 | [1073741824, 1342177280) | 36 | 0 |
| 5 | [1342177280, 1610612736) | 31 | 0 |
| 6 | [1610612736, 1879048192) | 47 | 0 |
| 7 | [1879048192, 2147483648) | 27 | 0 |
| 8 | [2147483648, 2415919104) | 48 | 0 |
| 9 | [2415919104, 2684354560) | 40 | 0 |
| 10 | [2684354560, 2952790016) | 39 | 0 |
| 11 | [2952790016, 3221225472) | 29 | 0 |
| 12 | [3221225472, 3489660928) | 36 | 0 |
| 13 | [3489660928, 3758096384) | 30 | 0 |
| 14 | [3758096384, 4026531840) | 34 | 0 |
| 15 | [4026531840, 4294967296) | 39 | 0 |
| **Total** | **[0, 4294967296)** | **601** | **0** |

Every raw shard log was checked for a final summary with correct bounds, 268435456 checked seeds, internally consistent count of emitted first-word matches and zero `complete=1` records. The 16 shards consumed 218,179ms combined process wall-time across four CPU threads per shard, about 218 seconds sequentially.

## Independent positive controls

1. Verified scalar native initialization, full twist, and first output tempering against independent `std::mt19937` for exact integer seeds **0, 5489, 12345, and 4294967295**: 4/4 full reference checks passed at output indices 0,1,2,3,622,623. This guards the difference between the in-place reference twist and an incorrectly simultaneous twist.
2. NumPy's independent legacy `RandomState(12345)` seeds the native scalar MT, and after the first generated draw its `get_state()[1]` stores the first fully twisted 624-word register. With ring phase17, native coordinates S[2],S[3],S[4],S[622] are `08C742F5,27E2EB57,B06480FE,6196535A`. Rebuild the SFT with `-DH17_SYNTHETIC`, scan just [12336,12352), one thread: exactly one whole-coordinate hit, **seed12345, phase17, complete=1**, with no other first-word hit. This tests the actual full-stage and phase search.

To reproduce the complete source search, build the SFT with native C++17 optimization and AVX512F/AVX512DQ; execute each exact shard's [start,end) with four threads, then compare all 16 summaries and each `complete` flag. The SFT is pure computation with fixed original-source p951 controls; it does not touch evidence or keys. An AVX512-capable host is required.

## Interpretation and next action

The entire **native uint32 scalar initializer → exactly one full twist → arbitrary cyclic rotation → original p951 state** family is excluded by independently retained packet source words. It does **not** exclude a different number of twists, arbitrary intervening draws with unknown output routing, `seed_seq`, non-scalar initialization, CPython `init_by_array`, a different historical printer chronology, or an original paper/copy transition unrelated to the export stream.

The direct source-producing hypothesis yielded no new authenticated selected K04 bits, no complete physical coupon, and no K08 literal phrase. Further adjacent scalar-twist or seed-offset expansion without an independent original epoch cue is low-leverage. Prioritize the selected physical/capture mechanism, or a distinct source-derived whole-caption construction for K08. Official REC8/1 status remains six individual PASS; K04/K08 absent; combined INCOMPLETE.
