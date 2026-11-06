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

The source-only full original run (optimized 12-thread C++17) completed in approximately **17.47 wall seconds** in this invocation. A second independent Python/GF2 xoshiro128\*\* inversion and source scan reproduced the first model's seven first-lane matches and zero full source packet matches. Test source SHA256 `63cb5e21a9b7e48b99fc4e6db9662aa36a253cc18a9f4648c1b43da0378fe6e5` for the original local full-algebra SFT.

**Genuine planted generator controls:** Each of the three actual modeled generators emits a synthetic packet, discards exactly 17 generated outputs, and emits a second complete packet. The same first-packet state recovery and variable-gap search retrieves gap **17** and the entire second packet for each model. The full original source packet 0300 is reconstructed by the first-packet state inverses, providing a separate original-domain check. Only the original second packet fails.

## What is excluded

Under these *specific* compact-state output scramblers, within-packet consecutive geometry, four serializers, and a gap at most 2^32-1 outputs between jobs 0300 and 0301, **no shared persistent generator history can even explain the first two real 16-byte intact packets**. Any arbitrary later packet gaps, retry-specific exceptional stages or copy methods cannot rescue that already contradicted two-packet model. This significantly extends the earlier constant-skip negative without generating arbitrary K04 candidate values.

A different generator, independent reseeding between packets, variable draws *within* a packet, a larger initial state, or historical physical-copy transformations are not excluded. This conditional original-source negative authenticates no physical selected ACK2 bytes and makes no claim about Emily's terminal caption. Original K04/K08 missing; combined REC8/1 `accepted=false`.
