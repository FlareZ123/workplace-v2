# K04 compact-state printer producers with arbitrary variable interpacket gaps (6 November 2026)

**Agent 12 | Original source-only full second-packet rejection.** Six official REC8/1 components remain accepted; K04 and K08 missing; combined INCOMPLETE. This result does not recover a selected physical coupon bit. It is a new variable-skip hypothesis, not an attested historical printer implementation.

## New mechanism and source boundary

Existing [six-producer exact state inversion](h17-k04-six-prng-families-exact-state-inversion.md) tested only *constant* skip counts 0/1/2/3/4/8/16/32 between regular printer records. A batching or event-driven issuer may instead consume a different number of generator outputs between *each* printer packet. The first intact 16-byte packet itself fully determines the modeled post-packet state for three 128-bit compact-state generators, so the **first interpacket gap can be scanned without imposing any constant later-row schedule**.

Three frozen generators: standard **xoshiro128\*\*** (four scrambled 32-bit successive outputs), **xoroshiro128\*\*** (two scrambled 64-bit successive outputs), and **Marsaglia xorshift128** (four native 32-bit successive outputs, shifts 11/8/19). Four packet serializers per generator: 32- or 64-bit whole-word little/big endian and original/reversed word order. The original 07:00 job 0300, attempt1 ACK, and 07:05 job 0301, attempt1 ACK, are source-only anchors. All 128 ordinary jobs exist, but the test requires only these first two. The disputed 0417/18:02 RECOVER ACK2 is excluded completely from source fitting and matching.

Original source `resources/evidence/print/spool-reconstruction.log` SHA256 **`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`**. Authentic first packets `FBBBC54356483F5864BB3F06794518A5` and `64176B6C3A91BD06B12FC0D90B3A7DB4`. The first packet fixes 128 independent xoshiro128\*\* state equations; xoroshiro128\*\* unscrambling gives consecutive s0 values and uniquely recovers the missing s1 register; in xorshift128 the final four emitted words equal the exact post-packet state.

## Fully executed original-source variable-gap census

For every fitted first-packet state, enumerate **every integer gap 0..4,294,967,295**, advancing the real generator output function for that many discarded draws. Compare the full second authentic 16-byte packet, first using its first emitted 32/64-bit lane and then the remaining lanes. This is a complete **2^32-gap interval per orientation**, rather than a constant-gap cross-packet model. The global total is **51,539,607,552** gap/orientation assignments over twelve full candidate geometries, with inexpensive first-lane gating.

| Generator | Serializer views | Gap assignments per view | First-lane coincidences (all views) | Full second-packet matches |
| --- | ---: | ---: | ---: | ---: |
| xoshiro128\*\* | 4 | 4,294,967,296 | **7** (views big-forward=2, big-reverse=1, little-forward=3, little-reverse=1) | **0** |
| Marsaglia xorshift128 | 4 | 4,294,967,296 | **3** (big-forward=0, big-reverse=0, little-forward=1, little-reverse=2) | **0** |
| xoroshiro128\*\* | 4 | 4,294,967,296 | **0** (all four views) | **0** |
| **Total** | **12** | | **10** | **0** |

The [reproducible original-source C++17 test](../agents/agent12/k04_compact_prng_variable_gap_sft.cpp) freezes the exact original first-packet xoshiro128** GF(2) inverse, recalculates the xoroshiro128** inverse algebraically, reads the authentic first two packets, and performs the same twelve variable-gap scans. The source-only full original run (optimized 12-thread C++17) completed in approximately **17.47 wall seconds** in this invocation. A second independent Python/GF2 xoshiro128\*\* inversion and source scan reproduced the first model's seven first-lane matches and zero full source packet matches. Test source SHA256 `63cb5e21a9b7e48b99fc4e6db9662aa36a253cc18a9f4648c1b43da0378fe6e5` for the original local full-algebra SFT.

**Genuine planted generator controls:** Each of the three actual modeled generators emits a synthetic packet, discards exactly 17 generated outputs, and emits a second complete packet. The same first-packet state recovery and variable-gap search retrieves gap **17** and the entire second packet for each model. The full original source packet 0300 is reconstructed by the first-packet state inverses, providing a separate original-domain check. Only the original second packet fails.


## New role-specific target bridge: preserved RECOVER/bench whole-packet controls

The original selected north coupon is **PS-261003-0417, 18:02, RECOVER ACK attempt2, DEST=bench**. Two preserved packets bracket that event in the exact same printer class and destination, though with differing attempts: **0416/16:40 RECOVER ACK1/bench** `F1F5A127EA44F563935C63F8A59A2801` and **0420/18:25 RECOVER ACK2/bench** `432475F72A62DB39F3D5693E2C937FA4`. A third earlier same-role original is **0407/15:55 RECOVER ACK1/bench** `2E03FD9FBCB793A59401131BC16B2D45`.

This provides a materially stronger target-oriented independent source discriminator than two adjacent routine jobs: a shared selected-class emitter could first be validated on preserved whole packets, then its 0417-stage candidate would be reconstructed. Run the **same three independently invertible compact-state generators**, four serializers and **all 2^32 independently variable interpacket gaps**, separately for the chronology pairs **0407→0416** and **0416→0420**. The copied 0417 selected ACK2 bytes and original K04 target digest remain entirely excluded while determining whether any emitter passes.

| RECOVER/bench preserved source pair | Full generator/gap hypotheses tested | xoshiro first-lane matches | xorshift first-lane matches | xoroshiro first-lane matches | Whole second-packet matches |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0407→0416 | 51,539,607,552 | 4 | 2 | 0 | **0** |
| **0416→0420**, bracketing selected 0417 | 51,539,607,552 | 6 | 5 | 0 | **0** |
| **Both independent pairs** | **103,079,215,104** | **10** | **7** | **0** | **0** |

Executed locally on the unmodified original spool with exact SHA-pinned source, full algebraic 128-bit xoshiro inverses regenerated for each frozen cohort's **actual first packet**, xoroshiro 64bit inverse, xorshift128 post-packet state, and the same complete planted 17-gap positive tests. Both separate complete runs succeeded in approximately 16–17 seconds each. Source-pinned local SFT `h17_k04_bench_recov_gap_sft.cpp`, SHA256 `285343840e83a69eaffe97c696639575550e5e1e894d6a9be027f9d332201108`; its algorithm differs from the shared [portable ordinary-packet SFT](../agents/agent12/k04_compact_prng_variable_gap_sft.cpp) only in parsing fresh cohort originals and inverting the corresponding first packet. The local source script was independently compiled and executed for both pairs. Remote CI for this cohort-specific script has not been claimed.

**Decision:** even allowing *billions of nonconstant hidden draws*, these three 128-bit PRNG emitters fail **before the disputed selected coupon is considered**, on an actual nearby same-CLASS/DEST control. Thus the complete 0417 coupon cannot be defended as the prediction of a single coherent 0407/0416/0420 emitter of these particular kinds. This is still conditional: the surviving late ACK2 copy is not independently authenticated to the physical medium; an epoch reset, rekeying, within-packet variable output, different emitter, or selected-only printer stage remains open. Do not use a source-derived apparent producer as a physical K04 proof.


## Direct K04 attempt from the 0416 same-role predecessor (201,326,592 full commitments)

Despite failure to explain the independent 0420 ACK2 packet, there remains a weaker **one-epoch model** in which the original 0416 RECOVER/bench packet and the selected 0417 RECOVER/bench ACK2 share one generator before an unrecorded rekey/reset before 0420. It is an extra speculative assumption, explicitly **not independently source-attested**. Unlike the foregoing control-only exclusions, this branch constructs *entire complete candidate physical coupons* and tests the original K04 acceptance digest.

Start from the real 0416/16:40 RECOVER/bench ACK1 `F1F5A127EA44F563935C63F8A59A2801`; for each of the same 3 reversible generators and 4 serializer views, recover the entire internal 128bit state from this genuine full first packet. For **every individual next fourword/twoword sliding window** at output gaps **0..16,777,215**, serialize the entire 16byte future coupon with the fixed source model's packet layout; XOR `8556C8CB6140A7F9A5123AC7571BEE1C` and compare the whole SHA256 of those 16 component bytes with immutable original K04 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

**Executed 201,326,592 complete original K04 SHA256 candidate assignments**, **0 genuine commitment matches**. The same selected ACK2 copied buffer is **withheld from all state reconstruction**; it is used only as an explicit known failing target-check sentinel. The search uses two disjoint exact gap shards per view: 0..8,388,607 (**100,663,296 complete assignments**, 12/12 planted gap17 positives, 0 original matches) and 8,388,608..16,777,215 (another **100,663,296**, 0 original matches). OpenSSL SHA256 of all 16 original mask-XOR bytes executed on every complete candidate, never truncated comparisons. The local source-equivalent C++17 reproducer `h17_k04_bench_recov_target_sft.cpp` has SHA256 `77cf24038bdbd92a741b9d5438197814058a515c615e02b580666fab6263e1f0`; both shard logs and the full program remain in the current invocation's local evidence workspace. No remote CI run of the target search is claimed.

This is a genuinely new **full-component original K04 target sweep** in a role-specific, independently seeded compact-state model, beyond Agent37's shorter selected cross-slot 8192-window tests and earlier constant-gap printer producer tests. Its output set is **not claimed disjoint** from all earlier candidate families; individual complete coupon values could coincide. It excludes exactly these 12 fixed source/target serializer classes and 2^24 consecutive output windows. One-epoch resets, transformed/independently serialized selected coupons, larger hidden gaps, different generators or true physically corrupted 0416 source bytes remain open. The 0416→0420 source holdout independently warns this model is historically weak. No K04 physical original bit can be authenticated from the negative.

## What is excluded

Under these *specific* compact-state output scramblers, within-packet consecutive geometry, four serializers, and a gap at most 2^32-1 outputs between jobs 0300 and 0301, **no shared persistent generator history can even explain the first two real 16-byte intact packets**. Any arbitrary later packet gaps, retry-specific exceptional stages or copy methods cannot rescue that already contradicted two-packet model. This significantly extends the earlier constant-skip negative without generating arbitrary K04 candidate values.

A different generator, independent reseeding between packets, variable draws *within* a packet, a larger initial state, or historical physical-copy transformations are not excluded. This conditional original-source negative authenticates no physical selected ACK2 bytes and makes no claim about Emily's terminal caption. Original K04/K08 missing; combined REC8/1 `accepted=false`.
