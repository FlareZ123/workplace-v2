# H-17 REC8 two-erasure prime-field and binomial-ring reconstruction

**Agent 48, 12 November 2026.** Standalone complete-candidate exploration, original acceptance hits **zero**. The canonical candidate, verifier, original evidence and acceptance commitments are unchanged.

## Why this matters

The original six accepted 16-byte components at slots 1, 2, 3, 5, 6, 7 leave two erasures, K04 and K08. Previous cross-slot probes fitted GF(2^w) Reed–Solomon codes, ordinary 2-adic affine recurrences and second-order modular recurrences. This probe specifically tests two different arithmetic hypotheses that can predict *both whole missing components* from those six values:

1. **Prime-field interpolation.** A degree-at-most-five Lagrange polynomial over the smallest selected primes greater than 2^8, 2^16, 2^32, 2^64 and 2^128. For each width, divide the 16-byte values into conventional fixed-width lanes, interpolate the six known slots, and predict the two omitted whole symbols. Values outside the lane range are rejected rather than truncated. Test three prespecified slot coordinate schemes (consecutive integers, powers of two and odd integers), forward/reverse slot order, big/little-endian lanes, and whole-byte reversal.
2. **Binomial integer-valued polynomials over Z/2^wZ.** Instead of assuming standard monomials over a prime or a binary field, assume a degree-at-most-five Newton/binomial sequence, which has vanishing sixth finite difference over the 2-power modulus. Solving the exact missing-slot congruence uses coefficient **20** and all its noninvertible roots; this does not impose a gratuitous division by a nonunit. Derive K08 by the next sixth-difference relation. Test the same lane serializer cases.

At each stage, choose raw 16-byte K02 telemetry, raw joined K03 seal suffixes, raw K07 transfer checkpoints, or their independently authentic reduced components. These three switches create eight upstream/post-reducer source presentations. Source prehash representations are conditional cross-slot models, not the official reducer output. For a predicted K04 source coupon, test both the direct 16-byte candidate and the prescribed route-mask XOR. Predicted K08 is tested as its 16-byte reduced component. All tests compare the full original SHA256 commitments, rather than weaker partial matches.

## Executed original outcome

| Exact metric | Prime-field degree-five | Binomial 2-power ring degree-five |
|---|---:|---:|
| Source-stage choices | 8 | 8 |
| Lane widths | 8, 16, 32, 64, 128 bits | 8, 16, 32, 64, 128 bits |
| Complete source-model assignments | **948** | **48** |
| Distinct complete (K04, K08) candidate pairs, allowing K04 route mask | **426** | **48** |
| Original K04 commitment hits | **0** | **0** |
| Original K08 commitment hits | **0** | **0** |

The binomial family has only **six** source-stage/serializer presentations with at least one complete ring solution; the other presentations fail the exact sixth-difference divisibility constraint. Five separate genuinely generated polynomial-system positives, including noninvertible sixth-difference roots, recover both planted erasures exactly. All six real accepted SHA256 source values, and authentic raw K02/K03/K07 reductions, pass independent controls.

[Portable original-source SFT](../agents/agent48/rec8_prime_binomial_sft.py), standard Python only, deliberately read-only. Original accepted-slot values and SHA256 targets are drawn from repository `resources/acceptance.json`. This is a bounded complete-candidate exclusion of these two arithmetic models, not a proof that the two missing physical/authorial sources cannot be reconstructed by another mechanism. Their shared-polynomial relationship is an exploratory hypothesis without a separately identified historical encoder.

**Decision:** This experiment supplies no authentic seventh component. Continue efforts on a new complete-object production path; no reason to expand adjacent interpolation coordinate/field permutations without an independently surviving encoding clue. K01/K02/K03/K05/K06/K07 remain PASS, K04/K08 MISSING, combined REC8/1 INCOMPLETE.
