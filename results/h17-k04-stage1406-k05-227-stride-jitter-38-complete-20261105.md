# K04: stage1406 K02 and 38 additional +/-1-jittered four-latch K05 geometries, complete coupon negative

**Agent25 | 5 November 2026 | 11,040 distinct original complete K04 components tested, zero matches.** This is a new target-reaching extension of [the stage1406 exact-227 SFT](h17-k04-stage1406-k02-k05-sparse227-complete-coupon-20261105.md), which tested five geometries and 8,800 other complete K04 component values. Existing six REC8/1 slots K01/K02/K03/K05/K06/K07 remain PASS. K04/K08 remain unresolved, combined key INCOMPLETE.

## New original-specific proposal

The original K05 component is four separate CRC-valid node49 recorder latches, rather than a single physically atomic coupon, so a hypothetical shared generator may insert an extra value or miss one output between adjacent recorder latches. Under the conditional p951 native-MT model, consider **four independently selected original K05 word values** placed close to a 227-word stride, with offsets at most one native output from each of the previously identified source-sensitive stages. This tests a physically different possibility from the exactly 227-separated branch. No original producer log confirms such a stream, stage, or clock-to-draw mapping.

Original full-source selection remains unchanged: 132 intact printer packets (selected ACK row129 excluded) rank15,365; K02 maximum-revision GOOD/HOLD prehash `E1A5E474BAD7E853A2E8C71D3317D507` source-compatible in 10 of 16 presentations at hypothetical native MT stage1406; original K05 CRC-valid highest selected source latches `FF8B78200A56E8586DCDA00EF01E4572`. Both source objects independently reproduce their original acceptance commitments. The copied selected ESC-N 18:02 ACK2 row is wholly absent from model fitting.

## Independent source-only rank screen

Take each baseline first-K05 native stage q in `1120,1347,1516,1743,2139`. Enumerate `first = q-1,q,q+1`; independently perturb each of the three later latch positions by -1, 0, or +1 from `first+227,first+454,first+681`. This defines **5×3×3³ = 405** exact source-stage hypotheses. With *only original printer+K02 source equations*, compute the complete selected K04 target rank after hypothetically inserting all four native K05 words. This does not use K05 bytes, original K04 commitment, copied ACK or source acceptance selection to choose layouts.

| Remaining K04 unknown bits | Number of 405 geometries |
| ---: | ---: |
| 2 | 18 |
| 3 | 24 |
| 4 | 1 |
| 29 | 2 |
| 30 | 14 |
| 31 | 21 |
| 32 | 23 |
| 33 | 302 |

Of the **43 layouts leaving at most4 bits**, exactly five are the previous exact 227-stride baseline. The **38 new low-dimensional layouts** form the complete, predefined hypothesis family for this experiment. All 38 are retained in the reproducible source-rank construction; source RHS and target were not consulted when selecting these stages.

## Complete authentic K05 and K04 execution

At each of the 38 new layouts, for every one of the ten source-compatible real K02 presentations, test all `4! =24` independent K05 latch permutations and four byte-endian/native-or-tempered interpretations for **each** latch (`4^4=256`). Per layout this is `10×24×256=61,440` original K05 source presentations, or **2,334,720 total**. Actual source compatibility is assessed by complete GF(2) left-nullspace constraints before constructing K04 candidates. Efficient factorization of all source parity syndromes by original latch/position exactly preserves this compatibility check; it is algebraically equivalent to testing every full 128bit assignment.

**Observed result:**

- **676,400** original K05 presentation assignments satisfy all fixed printer+K02 source equations in these new layouts.
- Their complete remaining two- or three-bit K04 quotient assignments produce **11,040 distinct full 16-byte K04 components**. The original route mask is applied to the four tempered little-endian native output words for every candidate.
- The original full K04 SHA256 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0` matches **zero** of those complete candidates.
- **380/380** full-state seeded positive controls pass: ten source-compatible K02 modes times38 new layouts. Each positive instantiates a full symbolic state consistent with all historical printer and K02 observations, derives the prospective exact four K05 native outputs, and recovers its withheld selected packet in the correct `2^d` quotient. These are implementation controls, not evidence that the original cross-record producer existed.

The complete locally executed source-equivalent portable Python checker returned:

```text
JITTER_MODELS 38
SOURCE original printer rank 15365 selected K02 modes 10
ASSIGNMENTS_SUM 2334720 SOURCE_COMPATIBLE_SUM 676400 SYNTHETIC_FULL_COUPON 380
UNIQUE_COMPLETE_K04 11040 ORIGINAL_K04_HITS 0
```

Read-only reproducer: [`agents/agent25/k04_stage1406_k05_sparse227_jitter_target_sft.py`](../agents/agent25/k04_stage1406_k05_sparse227_jitter_target_sft.py), importing [Agent25 source-selector/rank](../agents/agent25/k04_stage1406_k05_target_rank_sft.py) and [Agent49 native-MT source model](../agents/agent49/k04_p951_symbolic_basis.py). Manual CI confirmation: [workflow](../.github/workflows/agent25-stage1406-sparse-jitter-sft.yml). This checks exact 405 original-source geometry ranks and asserts all candidate counts; original archive, checker, route mask and candidate untouched.

**Scope:** This is an exhaustive negative of the stated 38 source-sensitive jittered layouts under the speculative stage1406 shared-MT model, not a discovery of 128 physical coupon bits or a general exclusion of nonuniform recorder emissions. It adds to the earlier five-stage negative without repeating it; stage1406 ten-coset 85.9-billion original K04 SHA sweep is independently owned by Agent18. K08 author-final text remains a separate unresolved source problem.

## Independent clean GitHub Actions reproduction

[Manual original-source run 42125542257](https://github.com/FlareZ123/workplace-v2/actions/runs/42125542257) was dispatched against the newly committed portable reproducer and **completed SUCCESS at 22:56 UTC, 5 November 2026**. It independently checked the exact 405 stage-geometry source-rank histogram, all ten original source-compatible K02 modes, the authentic 2,334,720 K05 presentations, the zero real K04 matches, the 11,040 distinct candidates and all 380 planted positives in the repository's fresh checkout. This confirms the committed script's portable reproduction without relying only on the local precursor.
