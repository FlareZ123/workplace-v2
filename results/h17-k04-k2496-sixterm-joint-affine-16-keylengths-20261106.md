# K04: six exact source-affine initialization terms exclude 16 genuine CPython integer seed lengths at k2496

**Agent 23 | 6 November 2026 | complete original-source computation and genuine seeded controls PASS. K04 and K08 remain missing.**

## Observation: recover the joint source equations, not merely independently fixed bits

The 132 intact original printer packets in `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, provide 16,896 observed bit equations on a conditional 624×32-bit native MT19937 initial state at original printer chronology p951. Their GF(2) rank is **15,365**. The disputed selected physical coupon, row129, is excluded **before fitting**; no K04 target digest, route mask, copied payload, or accepted-key result is used to construct the source constraints.

The important new mathematical method is an *exact affine projection* onto a small set of initialized-state words. Eliminate all coordinates **outside** the requested words first, retaining right-hand sides, then enumerate the free source-supported bits within the requested word group. This recovers both intra-word and **cross-word** parity equations hidden by the older independent fixed-bit source masks. Each projection is a complete affine set, rather than a probabilistic or sampled word list. Its rank is obtained by subtracting the rank of the outside-word projection from the full observed rank. Source-derived observations never depend on the disputed copied selected ACK.

Under genuine Python `random.Random(integer)`, with the first output after *2,496 actual prior 32-bit outputs*, the source-supported initialized-state domains at the specific native p951 printer geometry are:

| Observed register group | Independent supported source equations | Free bits | Complete allowed tuples |
| --- | ---: | ---: | ---: |
| `S2,S3,S4` | 87 | 9 | 512 |
| `S8` | 29 | 3 | 8 |
| `S8,S9` | 58 | 6 | 64 |
| `S8,S9,S10` | 87 | 9 | 512 |
| `S16,S17,S18` | 88 | 8 | 256 |
| `S27,S28,S29` | 87 | 9 | 512 |

Additionally, original S6 and S7 are exactly `E403BB7D` and `1F7B301F`. These are observations of a **hypothetical native MT19937 chronology**, which has not been established as historical printer firmware. The source packets and the projection equations themselves are original preservation material.

## Complete source-derived first-pass CPython term sets

For genuine CPython `init_by_array`, define unsigned 32-bit operations:

```text
G_i: standard 19650218 seeded initialization array
F1(x) = 1664525 * (x XOR (x >> 30)) mod 2^32
F2(x) = 1566083941 * (x XOR (x >> 30)) mod 2^32

A_i = (S_i + i) XOR F2(S_{i-1})           for i >= 2
T_i = A_i - (G_i XOR F1(A_{i-1})) mod 2^32
    = key[(i-1) mod n] + ((i-1) mod n) mod 2^32
```

Here `A_i` is the **first-pass** array and `S_i` is the final initialized state after the second pass. All selected indices are before CPython's special first-pass index1 wrap. `T_i` denotes a seed key-array term, **not** archive recovery slot K04.

The six source-affine domains above, with fixed S6 and S7 for the T8 and T9 cases, yield all possible complete 32-bit values of:

| Exact term | Corresponding source words | Distinct possible values |
| --- | --- | ---: |
| T4 | S2,S3,S4 | 512 |
| T8 | S6,S7,S8 | 8 |
| T9 | S7,S8,S9 | 64 |
| T10 | S8,S9,S10 | 512 |
| T18 | S16,S17,S18 | 256 |
| T29 | S27,S28,S29 | 512 |

**Every one of the 15 different pairwise intersections of these six original-source term sets is empty.** This was checked by an actual complete source-affine enumeration in the archived SFT and an independent local original projection. The observation is stronger than comparing fixed bits or checking individual guessed seeds.

For genuine key-array length n, `T_i=T_j` is compulsory whenever `(j-i) mod n=0`, because the two terms use the same key word *and* the same index-dependent additive residue. The fifteen differences are `4,5,6,14,25,1,2,10,21,1,9,20,8,19,11`. Their positive divisors include the **16 distinct seed word lengths**:

```text
1,2,3,4,5,6,7,8,9,10,11,14,19,20,21,25
```

Each value is therefore **completely excluded** for CPython integer seeds under the fixed p951, true prior-output offset2496 model. This covers multiple 32-bit to 800-bit seed representations, with no direct 2^(32n) seed brute force and no commitment-assisted inference. Other lengths such as n12, n13, n15 and n>=26 are **not excluded** by this result.

## Executed original data and positive controls

The [manual independent GitHub Actions run 42310648562](https://github.com/FlareZ123/workplace-v2/actions/runs/42310648562) completed SUCCESS on the committed original archive checkout. Its source-pinned Python SFT:

1. Constructs all original 132 selected-withheld printer packet equations, including their actual RHS, and the six complete affine word-group domains.
2. Independently constructs 16 genuine CPython `random.Random(integer)` initial states of the sixteen key word lengths from known arbitrary seeded words and confirms the required repeated-term identities. **16/16 PASS.**
3. For representative true lengths n1, n7, n11 and n25, generates 133 authentic native CPython printer packets at the declared 2,496 output offset, withholds synthetic row129, recomputes every synthetic-source domain, and checks the genuine initialized state is present and repeated seed term represented. **4/4 complete historical-layout synthetic control witnesses PASS.**
4. Tests the actual original 15,365-rank source and its 15 complete pairwise intersections, all zero.

Exact terminal execution summary:

```text
GENUINE_CPYTHON_16_LENGTHS_REPEATED_KEYTERM_CONTROLS=16/16 PASS
GENUINE_CPYTHON_FOUR_FULL_SOURCE_DOMAIN_WITNESSES=4/4 PASS
ORIGINAL_SELECTED_ROW129_WITHHELD_SOURCE_RANK=15365
ORIGINAL_JOINED_AFFINE_TERMS T4=512 T8=8 T9=64 T10=512 T18=256 T29=512
ORIGINAL_ALL_15_PAIRWISE_SOURCE_TERM_INTERSECTIONS=ZERO
ORIGINAL_INTEGER_KEY_LENGTHS_EXCLUDED=1,2,3,4,5,6,7,8,9,10,11,14,19,20,21,25
ORIGINAL_CPINT_K2496_16_SEED_WORD_LENGTHS_EXCLUDED=PASS
```

Source and reproduction: [six-term source-only test](../agents/agent23/k04_cpython_k2496_sixterm_joint_sft.py), [manual Actions workflow](../.github/workflows/h17-agent23-k2496-sixterm-affine.yml), [successful run](https://github.com/FlareZ123/workplace-v2/actions/runs/42310648562).

## Supporting independent tests

- [Unified n1..6 original joint-source theorem](h17-k04-k2496-joint-affine-source-n1to6-20261106.md), six seeded full-packet controls and original source [CI run 42309858527](https://github.com/FlareZ123/workplace-v2/actions/runs/42309858527).
- [Exact complete 64-bit n2 k2496 seed inverse](h17-k04-cpython-k2496-n2-complete-inverse-20261106.md), 32 shards all successful, zero source S16 survivors, [run 42305978745](https://github.com/FlareZ123/workplace-v2/actions/runs/42305978745).
- [N3 and n4 independent exact original source-domain inversions](../agents/agent23/k04_cpython_k2496_n3_worddomain_sft.py), genuine full-packet seeded controls and original source [run 42308721893](https://github.com/FlareZ123/workplace-v2/actions/runs/42308721893).
- [N5 separate repeated-term source-domain test](../agents/agent23/k04_cpython_k2496_n5_repeat_sft.py), synthetic positives and original [run 42309510604](https://github.com/FlareZ123/workplace-v2/actions/runs/42309510604).
- [N6 independent six-word inverse](../agents/agent23/k04_cpython_k2496_n6_wordjoin_sft.py) links two 262,144-sized complete source word domains using a repeated key term, finds 16 original source tuples, and has zero additional original S5-compatible six-word keys. Final corrected [manual run 42309925932](https://github.com/FlareZ123/workplace-v2/actions/runs/42309925932) succeeded, including real planted source controls. Two earlier failed runs were resolved by extending the initializer-prefix length and using the synthetic S5 RHS in synthetic controls.

These are corroborating conditional tests, not confirmations of the historical printer firmware. The above six-term result is a stronger and cheaper source-only exclusion mechanism for the sixteen stated seed lengths.

## Limits and next questions

**No original selected physical K04 coupon bit was recovered**, the selected paper/capture stage remains unauthenticated, and the K08 author's exact final caption remains unquoted. The six established REC8 archive components remain PASS and the combined original verifier remains INCOMPLETE. The main new information is a **mathematically source-attested relation** that decisively rejects particular speculative CPython seed lengths under one presumed printer chronology. Do not extrapolate it to other true offsets, native stage geometries, software RNG implementations or longer integer seeds.

Future work may reuse the exact source-affine projector at *other historically motivated* generator offsets or look for further finite term sets supporting a whole selected-value prediction. An actual original selected paper copy or exact author-final margin would bypass this conditional producer limitation.
