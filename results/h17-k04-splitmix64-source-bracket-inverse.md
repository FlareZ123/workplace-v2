# K04: reversible SplitMix64 same-job source-bracket test

**Agent 7 | 3 November 2026 | 8 complete K04 predictions rejected, source history independently incompatible.**

## New testable mechanism

The preserved printer log holds two full, nonselected, same-job RECOVER packets around the disputed selected 18:02 ACK2: `PS-261003-0417` REQUESTED attempt1 at 18:01 and REQUESTED attempt3 at 18:03. Treat each 16-byte packet as two consecutive 64-bit outputs of a reversible integer-mixing generator; the selected attempt2 would consume two unseen outputs in between. Unlike preceding xorshift128+ and xoshiro256** bitvector inversion, the proposed SplitMix family has an **algebraically reversible 64-bit output permutation** and can be solved directly from the first two words, with the **per-instance additive step gamma unknown**.

The primary mixer is the original Stafford-13 SplitMix64 function used by Apache Commons RNG and Java 8 SplittableRandom: 30/27/31 shifts with multiplication constants `BF58476D1CE4E5B9` and `94D049BB133111EB`. A distinct MurmurHash3 64-bit finalizer variant, with 33/33/33 shifts and constants `FF51AFD7ED558CCD`, is also tested as an alternative *hypothetical reversible producer* (it is not claimed to be the historical printer implementation). Examine both 64-bit endian serializations, with both orders of the two words, for eight source-stage layouts.

For each layout, invert each first-attempt 64-bit word to states `s0,s1`, and infer `gamma=(s1-s0) mod 2^64`. For an odd `gamma`, any single uninterrupted SplitMix stream, regardless of the number of hidden **whole outputs** between packets, requires the two inverse states of attempt3 to differ by that same gamma. This is a source-only necessary condition, independent of the missing selected bytes and of the acceptance commitment. Independently construct the complete middle 16-byte coupon from `mix(s0+2gamma)` and `mix(s0+3gamma)`, apply the unchanged route XOR mask, and check original K04 acceptance. These checks need no brute-force seed or hidden-gap bound.

## Actual result

- The source SHA256 pin for `resources/evidence/print/spool-reconstruction.log` passes: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- **48/48 genuinely generated positive controls** pass: two mixers × two byte orders × two word orders × three seeds × two odd gammas. All recover the complete synthetic missing packet exactly, with the fixed-step distinction correct.
- The **128 ordinary intact printer packets** contain zero single-packet matches to the fixed golden-ratio gamma in all eight layouts: **0/1024**.
- The two original same-job intact retry packets yield **0/8** compatible same-gamma stream histories even allowing an arbitrary odd gamma and an unbounded number of complete hidden output steps.
- The eight complete middle-coupon predictions obtained from attempt1 alone yield **0/8 original K04 SHA256 matches**, after the original mask XOR. This commitment test is subordinate to the source contradiction; its failure is an additional finite observation, not a recovery claim.

Portable, source-pinned, read-only standard-library reproducer: [`agents/agent7/k04_splitmix64_retry_sft.py`](../agents/agent7/k04_splitmix64_retry_sft.py). Original 18:02 copied ACK bytes are deliberately excluded from all producer fitting. Original evidence, route mask, acceptance, verifier and candidate were not modified.

## Scope

This exact reversible two-64bit-output per packet source architecture is falsified before the missing output would be selected. The test does not exclude a changed gamma between attempts, a per-attempt new seed, unequal gap *inside* a packet, byte mixers applied after the raw generator output, independently generated physical coupon contents, or an unrelated producer. It contributes **zero authenticated historical K04 coupon bits**. K08 final wording also remains unobserved. Original K01/K02/K03/K05/K06/K07 remain PASS, while K04/K08 are MISSING and combined REC8/1 remains INCOMPLETE.

External algorithm references: [Apache Commons RNG SplitMix64](https://commons.apache.org/proper/commons-rng/commons-rng-core/jacoco/org.apache.commons.rng.core.source64/SplitMix64.java.html) and [OpenJDK Java 8 SplittableRandom](https://code.googlesource.com/edge/openjdk/+/refs/heads/jdk8u111-b14/jdk/src/share/classes/java/util/SplittableRandom.java).
