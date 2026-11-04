# H-17 K04: source-only algebra eliminates all 624 NumPy pool4 second-cycle start phases

**Agent 2 | 4 November 2026.** An independently executed, source-pinned calculation eliminates **all 624 phases** of the hypothetical NumPy `MT19937(SeedSequence)` **second-cycle** printer generator. Earlier [Agent33's full second-cycle SMT pilot](h17-agent33-numpy-secondcycle-new-heldout-pilot-20261103.md) examined just phases 0..392, obtaining 187 definitively UNSAT and 206 UNKNOWN. This new direct GF(2) source-word/pool4 inversion produces **0 surviving phases for 0..623**, without SMT and without consulting the K04 target commitment or disputed selected row. The result is a *conditional producer-class exclusion*, **not** a reconstructed original physical K04 coupon.

## New method: anchor at the genuine initialized register, project source-fixed words, invert entropy pool

Original retained printer log SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The conditional p951 printer row-start chronology has 133 rows. **Row129**, PS-261003-0417 / RECOVER / 18:02 ACK2, is omitted from every basis equation. Only the other **132 intact 16-byte printer packets** are used. The resulting 528 tempered output words yield **15,365 independent GF(2) source equations** for an MT19937 initialized register.

For an assumed NumPy second-cycle start phase `p=0..623`, the native source stage `s` corresponds to NumPy raw output index `603+p+s`: original row3 has source stage22 and would be raw output `625+p`, i.e. second MT cycle phase p. **Crucial correctness detail:** set symbolic register origin at `s=-1226-p` so stage `origin+i` is NumPy's *actual initialized* `K[i]`. Applying MT recurrence backward before this origin creates spurious constraints, because an initialized register is not generally a valid earlier MT history. This anchored inversion avoids that artifact; eleven genuinely initialized NumPy histories pass.

For each phase independently:

1. Build 624 unconstrained 32-bit initialized register words `K[0..623]`, with standard MT recurrence thereafter. Insert all 528 intact source native-word observations into a consistent rank-15,365 GF(2) basis.
2. Project every initialized word against the fitted source basis, obtaining exactly the independently known bitmask and value. The phase-dependent number of fully fixed 32-bit register words ranges roughly 60..132 in the observed original and 66..132 in the synthetic controls.
3. NumPy forcibly overwrites `K[0]=0x80000000`. Any independently fixed contradictory K0 bit eliminates the phase.
4. Otherwise, invert the standard NumPy default four-word SeedSequence pool whitening for every fully fixed `K[i]`, `i>=1`. With `b_i = INIT_B * MULT_B^i mod 2^32` and `f_i = b_i*MULT_B mod 2^32`, define

   ```text
   z_i = K[i] XOR (K[i] >> 16)
   P[i mod 4] = (z_i * inverse_mod_2^32(f_i)) XOR b_i
   INIT_B=0x8B51F9DD, MULT_B=0x58F38DED
   ```

   The multiplier is odd, hence invertible. Every source-fixed word with equal index mod4 must yield **identical** 32-bit pool contents. A mismatch proves no possible 128-bit pool could have produced the original intact source at that phase. If all fully fixed entries agreed, compare all partially fixed K words to pool-generated values as a final check.

This eliminates the 128-bit entropy pool *symbolically* from the original source. It does not need a guessed seed, NumPy entropy list, SMT solver, truncated candidate corpus, route mask, or original SHA256 K04 commitment.

## Exact original source results

Five local disjoint runs covered all 624 phases:

| Source phase interval | Contradictory overwritten K0 | Contradictory repeated pool word | Compatible phases |
| --- | ---: | ---: | ---: |
| 0..189 | 17 | 173 | 0 |
| 190..279 | 9 | 81 | 0 |
| 280..392 | 21 | 92 | 0 |
| 393..499 | 12 | 95 | 0 |
| 500..623 | 16 | 108 | 0 |
| **Total 0..623** | **75** | **549** | **0** |

In every phase the 132 source packets are internally GF(2)-consistent with rank 15,365. Thus these contradictions are specific to the **NumPy seeded initial-state family**, rather than a generic MT printer-source contradiction.

**Real-generator positive controls:** Eleven independent `numpy.random.MT19937(seed)` streams were constructed from actual NumPy `SeedSequence` values at phases `0,13,99,218,390,392,393,500,619,620,623`; all reproduced rank15,365, all projected register bits agreed with NumPy's actual initialized key, every fully fixed pool word inverted to the exact true pool, and **all eleven survived** the exclusion gate. This includes the last five phases outside the earlier 0..392 SMT analysis and the wrapped second-cycle 620..623 boundary.

The [read-only portable single-file test](../agents/agent2/k04_numpy_secondcycle_pool4_fullphase_sft.py) contains original source SHA assertion, independent NumPy-generated synthetic controls, every original phase, and a final count assertion. The [manual-only GitHub Actions workflow](../.github/workflows/agent2-k04-numpy-pool4-fullphase-manual.yml) reproduces it with NumPy 2.3.5. The source-pinned local runs completed successfully before publication; remote CI status can be checked separately.

## Historical interpretation and future attack

**Eliminated precisely:** the standard NumPy `MT19937` initialized by the standard default pool4 `SeedSequence`, with original printer chronology p951 and row3 assigned to one of the 624 positions of the *second* MT output cycle, fixed conventional little-endian 32-bit word serialization, using all 132 unselected intact rows as outputs of one such generator.

**Remaining:** other actual producer families, NumPy custom pool sizes, seeds injected via nonstandard key initialization, output cycles later than the second, alternate spool chronology/byte serializer, multiple independent generators, exceptional copied ACK media errors. The historical printer firmware has not been authenticated as NumPy, so this negative does not itself determine a selected coupon byte.

**Recovery impact:** K04 original physical coupon bits authenticated **0/128**, K08 exact author-final words **0**. Original six slots continue to PASS individually, combined REC8/1 remains INCOMPLETE. With the 206 earlier SMT UNKNOWN second-cycle cases now algebraically excluded, researchers should avoid another larger SMT timeout replay of this precise NumPy pool4 model. Look instead for historically linked complete-coupon construction or author-final caption lineage.

## Reproduction

With NumPy installed, run the SFT from the repository. The no-argument invocation tests all 624 source phases; two optional integer arguments specify a half-open phase interval, allowing the five independently executed ranges in the table. Original resources, K04/K08 hash commitments, canonical candidate and verifier remain unchanged.
