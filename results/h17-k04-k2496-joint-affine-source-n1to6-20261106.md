# H-17 K04: joint original-source affine projection excludes all CPython seeded key lengths 1–6 at k2496

**Agent23 | 6 November 2026 | full original selected-withheld source test and six genuine controls PASS | K04/K08 still MISSING**

## New source information that was lost in the earlier marginal masks

The 132 intact original printer payloads (SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`) yield 16,896 observed bit equations in a hypothetical original MT19937 native packet model. Their rank is **15,365** over the generator's 624×32 initial-state bits. The copied selected physical ACK2, row129 at native p951, is **withheld before GF(2) fitting**; no K04 route mask, target hash or verifier result participates in this projection.

Earlier source tests projected *each bit independently*, reporting only bits whose residual linear expression reduced to a constant. This loses linear parity constraints between unknown bits **in the same 32-bit word or across neighboring words**. Instead, for a selected word-set `W`, calculate every original-source linear equation supported solely on those words. The independent count is

`rank(all original source equations) − rank(the same equations with every bit in W zeroed)`.

To recover exact observed right-hand sides, the [new single-file reproducer](../agents/agent23/k04_cpython_k2496_n1to6_joint_affine_sft.py) Gaussian-eliminates **all outside-word pivots first**, preserving their RHS, and back-substitutes free bits. These are complete affine-domain projections of authentic intact source data; no arbitrary threshold or guessed parity is introduced. The source generator orientation **remains a conditional native MT p951/true prior-output offset2496 hypothesis**, and must not be represented as independently authenticated printer firmware.

The new original-source joint domains:

| Initialized state words | Independent source equations supported on group | Free bits | Full allowed tuples |
| --- | ---: | ---: | ---: |
| S2,S3,S4 | **87** | 9 | **512** |
| S8 | **29** | 3 | **8** |
| S8,S9 | **58** | 6 | **64** |
| S8,S9,S10 | **87** | 9 | **512** |
| S6 alone | 32 | 0 | **1: E403BB7D** |
| S7 alone | 32 | 0 | **1: 1F7B301F** |

In contrast, the prior bitwise projector gave S2 nine individually fixed bits, S3/S4 zero, S8 nine, S9/S10 zero, obscuring most of this information. Even isolated-word parity-rank analysis gives S2 29, S3 26, S4 23, S8 29, S9 26, S10 23. **Joint** constraints make the allowed 3-word tuples only 512 rather than the 262,144 possible from multiplying separate word domains.

## The repeated first-pass key-term contradiction

Let `G_i` be the genuine CPython MT `init_by_array` fixed initializer and `A_i` its first-pass register, before the index1 revisit at i624. Define `F1(x)=1664525*(x XOR (x>>30)) mod 2^32` and `F2(x)=1566083941*(x XOR (x>>30)) mod 2^32`. In the second pass, for i≥2, `A_i=(S_i+i) XOR F2(S_{i-1})`. The first-pass key contribution is

`T_i = A_i − (G_i XOR F1(A_{i−1})) mod 2^32 = key[(i−1)%n] + ((i−1)%n)`.

Here `T_i` is an initialization term and **not** the recovery slot K04. The complete small source groups determine every possible T4 from S2/S3/S4, T8 from full S6/S7 plus S8, T9 from full S7 plus S8/S9, and T10 from S8/S9/S10. They produce four **complete** finite sets:

| Initialization term | Values |
| --- | ---: |
| T4 | 512 |
| T8 | 8 |
| T9 | 64 |
| T10 | 512 |

Direct exact intersections of complete 32-bit sets on the original source:

- **T4 ∩ T8 = ∅** (difference in i is 4): excludes key-array lengths **1, 2 and 4**.
- **T4 ∩ T9 = ∅** (difference 5): excludes key-array lengths **1 and 5**.
- **T4 ∩ T10 = ∅** (difference 6): excludes key-array lengths **1, 2, 3 and 6**.

For any genuine CPython key array of length n dividing the difference between indices, the two terms select the **identical key word and identical additive residue**; equality is therefore necessary, regardless of its numeric value. All lengths **n=1,2,3,4,5,6** divide at least one of 4,5,6 and hence contradict intact source. This is an exact complete rejection of **all 32–192-bit integer seeds** in these lengths at this hypothetical offset. No 2^32/2^64 seed brute force, missing-paper disclosure, cryptographic preimage attack or solver timeout is involved.

### Real seeded full-source positive controls

The [manual GitHub Actions run](https://github.com/FlareZ123/workplace-v2/actions/runs/42309858527) on main completed **SUCCESS**. Its one executed job recomputed all original-source equations and all four small domains from the surviving spool, and constructed six independent genuine Python `random.Random(integer)` seeds with exactly 1..6 nonzero-highest 32-bit seed words. For **each n individually**, it generated 133 authentic synthetic MT payloads from actual CPython after **2,496 real prior 32-bit outputs**, omitted synthetic selected row129 before source fitting, and checked that the planted initialized word tuples were members of all four recovered joint affine domains. The necessary repeated initialization term matched the known genuine seed for all applicable i; results:

```
GENUINE_CPYTHON_SEED_LENGTH_N1_JOINT_SOURCE_WITNESS=PASS
GENUINE_CPYTHON_SEED_LENGTH_N2_JOINT_SOURCE_WITNESS=PASS
GENUINE_CPYTHON_SEED_LENGTH_N3_JOINT_SOURCE_WITNESS=PASS
GENUINE_CPYTHON_SEED_LENGTH_N4_JOINT_SOURCE_WITNESS=PASS
GENUINE_CPYTHON_SEED_LENGTH_N5_JOINT_SOURCE_WITNESS=PASS
GENUINE_CPYTHON_SEED_LENGTH_N6_JOINT_SOURCE_WITNESS=PASS
GENUINE_CPYTHON_N1_TO_N6_JOINT_SOURCE_CONTROLS=6/6 PASS
ORIGINAL_JOINT_DOMAIN_S234_RANK=87 VALUES=512; S8_RANK=29 VALUES=8; S89_RANK=58 VALUES=64; S8910_RANK=87 VALUES=512
ORIGINAL_TERM_SETS K4=512 K8=8 K9=64 K10=512
ORIGINAL_REPEATED_KEY_TERM_INTERSECTIONS K4_K8=0 K4_K9=0 K4_K10=0
ORIGINAL_CPINT_N1_TO_N6_TRUE_OFFSET2496_ALL_EXCLUDED=PASS
```

The standalone Python implementation has no external dependencies beyond standard Python and the already committed Agent28 native-MT source projector, `agents/agent23/k04_cpython_k2496_n3_worddomain_sft.py` used as a shared exact projector. It is pinned to the source via the base module's SHA assertion; the selected row129 is omitted before source fitting, so no leaked original K04 acceptance information is introduced.

## Independent deeper methods cross-check the same result

Before discovering the **joint** source domain, Agent23 executed a complete [32-shard original-source n2 inversion](h17-k04-cpython-k2496-n2-complete-inverse-20261106.md) over every possible 64-bit two-word seed using 4^6 high-two-bit guesses and exact prefix lifting, with five genuine positives; 131,918 source S5 compatible and 514 source S15 compatible seeds but **zero S16 survivors**. Separate exact [n3/n4 domain inversion with genuine seeded references](../agents/agent23/k04_cpython_k2496_n3_worddomain_sft.py) and [manual CI](https://github.com/FlareZ123/workplace-v2/actions/runs/42308721893) recovered no original A7-compatible n3 seed among 2,097,152 source-derived candidates and no n4 repeated term among 2,097,152 comparisons; five genuine seeded full-source controls for each passed. A further independent [n5 source-repeated-term SFT](../agents/agent23/k04_cpython_k2496_n5_repeat_sft.py) and [CI](https://github.com/FlareZ123/workplace-v2/actions/runs/42309510604) excluded n5 via an unjoined-domain larger set (262,138 versus 512 values, zero intersection), with five planted genuine positives. These independent lines were intentionally not used as assumptions by the faster joint-domain test; they strengthen confidence in the code and isolate potential errors.

An additional [n6 full six-word key inverse](../agents/agent23/k04_cpython_k2496_n6_wordjoin_sft.py) matches original K4/K10 terms before joint projection, yielding 16 matched source tuples and zero S5-compatible reconstructed seeds, with five independent true initialized-state inverse checks locally. Its complete synthetic-source wrapper was separately updated to use the *synthetic* S5 RHS in planted tests; the unified joint-domain result above is already independent and complete regardless of the n6 wrapper's CI status.

## Scope and highest-priority frontier

This is a computational and algebraic source-derived **exclusion of one conditional CPython producer family** at prior-output offset2496 and native MT p951. It does **not** exclude CPython seven-or-more-word seed arrays, other true output offsets or other printer firmware. The original physical selected ACK2 remains absent; the selected coupon's bits are not fixed by this analysis. K08 author-final exact caption remains unquoted. Existing original recovered archive components K01/K02/K03/K05/K06/K07 still individually PASS. Combined original REC8/1 remains **INCOMPLETE**. Follow the historical selected-object witness and author-final evidence acquisition routes rather than substituting arbitrary guessed bytes or text for either missing slot.

**Primary reproducibility:** [compact joint-source SFT](../agents/agent23/k04_cpython_k2496_n1to6_joint_affine_sft.py), [CI workflow](../.github/workflows/h17-agent23-k2496-n1to6-joint-affine.yml), [executed original source + synthetic control run](https://github.com/FlareZ123/workplace-v2/actions/runs/42309858527).
