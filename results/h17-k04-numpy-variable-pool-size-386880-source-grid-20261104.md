# K04: NumPy SeedSequence custom entropy pool size versus source data, exact full grid

**Agent 2 | 4 November 2026.** Completed **386,880** exact, phase-anchored, *original-source-only* model tests for every second-cycle start phase `p=0..623` and every custom NumPy `SeedSequence(pool_size=d)` setting `d=4..623`. **Every possible pair with `d<=553` is inconsistent with the 132 intact printer packets.** The smallest pair that passes the necessary source test uses **pool_size=554**. In total **5,785** large-pool phase pairs survive the limited source test, with hundreds of unconstrained pool words, so **no physical K04 coupon can be reconstructed**. This extends the [earlier default-pool4 complete 624-phase exclusion](h17-k04-numpy-pool4-full-secondcycle-624-phase-exclusion-20261104.md) to a different initialization architecture rather than merely repeating its four-word comparison.

## Why the new producer class matters

NumPy officially allows `SeedSequence(entropy, pool_size=d)`; the default `d=4` gives a 128-bit pooled entropy, while `d=8` is also a supported larger-pool choice. A custom pool length is an actual NumPy API parameter, not an invented seed hashing scheme. The public [NumPy SeedSequence reference](https://numpy.org/doc/stable/reference/random/bit_generators/generated/numpy.random.SeedSequence.html) describes the parameter, and [NumPy MT19937](https://numpy.org/doc/stable/reference/random/bit_generators/mt19937.html) accepts a `SeedSequence` instance.

The preceding pool4 result proves there is no standard 128-bit NumPy pool initialization at any of 624 source phases under hypothetical p951 spool chronology. It does not cover larger entropy pools. A pool with eight or sixteen words, if historically used, could still produce a finite model tightly constrained by the preserved source and potentially predict the missing four-output coupon. The present experiment checks the complete finite family `d=4..623` rather than guessing seeds.

## Algebraic model and original-source controls

For each phase `p`, re-anchor the exact linear MT19937 symbolic recurrence at **initialized NumPy key K[0]** (native source stage `-1226-p`). Source-pinned spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Completely omit original selected `PS-261003-0417` ACK attempt2 row129 from all 528 original 32-bit output equations. Each source basis has exact GF(2) rank **15,365**.

Project individual initialized words `K[0..623]` against that basis. For every tested pool length `d`, all fully source-fixed `K[i]` imply their exact possible pool word `P[i mod d]` by inverting NumPy's index-whitened SeedSequence output transform. Reject the phase/pool combination if:

1. Any known bit of `K[0]` differs from NumPy's forced `0x80000000`;
2. Two independently source-fixed `K[i]` sharing residue `i mod d` demand different 32-bit pool words;
3. One fixed word derives a pool value, but another partially fixed `K[j]` at the same residue contradicts the predicted masked bits.

These are exact **necessary** checks for any arbitrary pool word values, even if a NumPy entropy input cannot realize a given entire pool. A surviving pair is not a confirmed actual `SeedSequence(entropy)` history. It is a non-eliminated model with an incomplete pool.

## Full original-source grid

Seven nonoverlapping executed phase shards cover every pair in `624 × 620`.

| Phase range | Pairs examined | Source-compatible large-pool pairs |
| --- | ---: | ---: |
| 0..39 | 24,800 | 230 |
| 40..139 | 62,000 | 639 |
| 140..249 | 68,200 | 931 |
| 250..364 | 71,300 | 1,089 |
| 365..489 | 77,500 | 1,284 |
| 490..554 | 40,300 | 591 |
| 555..623 | 42,780 | 1,021 |
| **Total** | **386,880** | **5,785** |

Exact rejection breakdown:

| Outcome | Original model assignments |
| --- | ---: |
| Contradictory initialized K0 bit | 46,500 |
| Two full K words demand incompatible same pool residue | 301,039 |
| Partial K-word constraint conflicts with derived pool | 33,556 |
| Survives necessary source test | 5,785 |
| **Total** | **386,880** |

**Zero survivors exist for any d in [4,553] at any of the 624 phases.** First potential survivors at d554 were found at phases 273, 280 and 282. A surviving pool of length554 contains **17,728 bits** before the high-level NumPy entropy mixing constraints. The original source fixes only a small fraction of its pooled words, so this compatibility is not a useful candidate for the selected K04 component.

**True-generator positive tests:** 19 different `np.random.MT19937(np.random.SeedSequence(seed,pool_size=d))` streams, with `d=4,5,8,16,19,32,37,61,64,101,127,128,256,301,511,512,523,601,623` and phases spanning the second cycle, each pass the same selected-withheld source gate. The actual independently generated `SeedSequence.pool` words match every inferred pool word. This is an essential guard against false exclusions from a guessed variable-pool law.

The [single-file original-source SFT](../agents/agent2/k04_numpy_variable_poolsize_fullgrid_sft.py) reuses the independently verified seeded register/source basis from the [pool4 SFT](../agents/agent2/k04_numpy_secondcycle_pool4_fullphase_sft.py), asserts all four full-grid outcome totals, and accepts independent half-open phase ranges. The [manual reproducibility workflow](../.github/workflows/agent2-k04-numpy-variable-pool-manual.yml) uses NumPy 2.3.5.

## Impact and limits

This finite source result demonstrates that a NumPy-style repeated entropy pool short enough to be predictive is inconsistent with the preserved printer data under this particular phase/serialization model. Only much larger unconstrained pools survive the source tests, which cannot supply the missing 16-byte coupon.

It does **not** show that NumPy was the printer's actual firmware, and it says nothing about a different PRNG, custom register seeding, later output cycles, corrupted copied records, multiple print devices, alternative phase chronology, or the physical ESC-N media. The `5,785` survivors have **not** been realized as independent NumPy entropy seeds or checked as full source histories, so should never be reported as reconstructed seeds.

**Decision:** Stop enlarging NumPy pool-length/source-only searches absent a physical firmware or seed provenance witness. The missing K04 output and K08 author-final text remain unverified, and there are **zero new authenticated K04 bits or K08 words**. The original six accepted REC8 components, acceptance hashes, verifier, and canonical candidate remain unmodified.
