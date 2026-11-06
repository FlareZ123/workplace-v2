# K04: complete CPython two-word source exclusion at genuine output offset 2496 by 32-bit inversions

**Agent 23 | 6 November 2026 | completed 32-shard exact original-source test; K04 remains MISSING.**

## A new solvable inversion after two previous symbolic-engine timeouts

At conditional printer native MT19937 packet chronology `p951`, the original printer spool `resources/evidence/print/spool-reconstruction.log` (SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`) provides 132 intact 16-byte packets. The disputed selected physical ACK2 is row129 and is **excluded before all GF(2) source fitting**. The exact source rank is 15,365. For a genuine CPython MT state after 2,496 prior native outputs, the initialized-state projection fixes:

| Word | Fixed-bit mask | Observed masked value | Bits |
| --- | --- | --- | ---: |
| S5 | `8000001F` | `00000011` | 6 |
| S6 | `FFFFFFFF` | `E403BB7D` | 32 |
| S7 | `FFFFFFFF` | `1F7B301F` | 32 |
| S8 | `09CC1C00` | `008C1000` | 9 |
| S15 | `000000FF` | `000000B6` | 8 |
| S16 | `5398BA7D` | `4010A820` | 18 |
| S17 | `01800800` | `00000800` | 3 |

The fixed S6/S7 imply complete first-pass `A7=((S7+7) XOR F2(S6))=2AED5290`, for `F2(x)=1566083941*(x XOR (x>>30)) mod 2^32`. Source rank, all printed values and these masks are reproduced from the original 132 packets by the included [single-file test](../agents/agent23/k04_cpython_k2496_n2_inverse_sft.py). This is the same original source geometry studied by [Agent1's source-forward result](h17-k04-cpython-k2496-shortforward-source-inversion-20261106.md), where Z3 and Bitwuzla returned UNKNOWN. The added S5 separate-key mask and a complete two-word algebraic inverse are new.

## Separate source constraints for the two 32-bit seed words

For CPython's genuine two-word integer seed `k0,k1`, denote first-pass state `A_i`, CPython initialization prefix `G_i`, and `F1(x)=1664525*(x XOR (x>>30)) mod 2^32`. Its recurrence, before the first-pass index1 wrap, is

```
A1 = (G1 XOR F1(G0)) + k0
Ai = (Gi XOR F1(A{i-1})) + (k0 if odd i else k1+1), i=2..7
Si = (Ai XOR F2(S{i-1})) - i, i=2..623
```

All operations are mod 2^32. Invertible `F1` and `F2` have odd multiplier inverses `F1^-1` using `0xFEE058C5` and `F2^-1` using `0x6A76AE6D`.

**Independently filter k0:** From known A7 and S6,

```
A6 = F1^-1(G7 XOR (A7-k0))
S5 = F2^-1(A6 XOR (S6+6))
```

Hence six source-fixed S5 bits depend solely on `k0`. **Independently filter k1:** From known A7 and S7,

```
A8 = (G8 XOR F1(A7)) + k1+1
S8 = (A8 XOR F2(S7)) - 8
```

Hence the nine source-fixed S8 bits depend solely on `k1`, leaving exactly `2^23=8,388,608` possible `k1` words in the full `2^32` domain.

For every retained `k1`, **exhaustively recover every k0** satisfying the complete A7 equality by guessing all six high-two-bit pairs of `A1..A6` (exactly `4^6=4096` cases). With the guessed pairs frozen, each proposed A7 congruence modulo `2^b` depends only on the low b bits of k0, so extend all possible prefixes one bit at a time, for b=1..32, **without branch caps**. Every actual pair has exactly one highbit-pattern case equal to its genuine A1..A6, so its k0 prefix survives all 32 congruences. Recompute A7 using real unguessed F1 at the end and reject spurious highbit guesses; this makes the enumeration complete. Source S5, then S15, S16, S17 are tested on these true full-A7 pairs.

The `k1` visit order `(x*0x9E3779B9) mod 2^32`, x=0..2^32-1, is bijective because its multiplier is odd; the 32 disjoint `2^27`-index intervals cover every k1 exactly once. This proves exact coverage of **all possible 64-bit two-word integer seeds**, without direct `2^64` enumeration. No assumptions about a secret seed distribution, probabilities, or heuristic branching are needed.

## Executed full-source result

Ran [manual 32-shard Actions workflow](https://github.com/FlareZ123/workplace-v2/actions/runs/42305978745) on a source-pinned repository checkout with the original selected ACK2 withheld. **All 32 jobs completed successfully** and their individual logs independently contained the expected `GENUINE_CPYTHON_TWO_WORD_COMPLETE_INVERSE=5/5 PASS` and `SHARD_NO_SOURCE_FORWARD_SURVIVORS`. Job-by-job logs were read from the Actions service and numeric totals independently summed.

| Successive exact source test | Complete count |
| --- | ---: |
| All k1 domain values scanned | **4,294,967,296** |
| k1 surviving original S8 nine-bit mask | **8,388,608** |
| Highbit guess cases evaluated | **34,359,738,368** |
| Full lowbit-lift roots before genuine highbits | **34,449,201,408** |
| Genuine full A7 roots with true F1 | **8,411,898** |
| Original S5 six-bit mask | **131,918** |
| Original S15 eight-bit mask | **514** |
| Original S16 eighteen-bit mask | **0** |
| Original S17 mask / all retained source packets | **0** |

The total measured worker execution inside numerical shards was ~5,203.784 aggregate job-seconds, distributed across 32 separate Actions jobs. An earlier local pilot x in [0,65,536) produced 140 S8-retained k1, 136 genuine A7 roots, one S5 survivor and zero S15/S16/S17, consistent with the complete execution.

**Genuine independent CPython references:** Seeds `(0x12345678,0x23456789)`, `(1,1)`, `(FFFFFFFF,FFFFFFFF)`, `(00001FC3,00001092)`, `(0,80000000)` were constructed using Python's actual `random.Random((k1<<32)|k0).getstate()`, not the tested expression. Each seeded reference passed the original-index firstpass A7 and S5/S8 inverse equations, and each was rediscovered exactly once by the exhaustive 32-bit inversion. The Python wrapper repeats these controls and pins the original spool SHA and source masks in **every shard**. Original S16 excludes all seeds; this is not a solver timeout or synthetic-only result.

## Exact scope of exclusion

This exhaustively **rejects CPython's genuine two-word integer-seed producer at true prior-output offset2496, conditional on native p951 MT chronology and the original 132 intact printed packets**. It complements [Agent23's complete offset2492/2493 n2 exclusions](h17-k04-cpython-k2493-two-word-bitlift-complete-20261106.md). Other offsets, key lengths, source-stage assignments or non-CPython printers are not excluded. A Python-like original physical printer issuer has not been authenticated. This new mathematical negative does not reveal any bit of the actual selected physical K04 coupon. K08 exact author-final desk-caption remains missing, the original six components remain accepted and combined REC8/1 remains **INCOMPLETE**.

If a future source-fitted key ever passes a related inversion, the wrapper predicts the **entire 132 intact records first**, then and only then computes the withheld selected full coupon and checks the untouched original K04 SHA256 acceptance commitment. Source evidence, route, original verifier, commitment and `candidate.json` were never modified.

Reproducible code: [C++ exact inverter](../agents/agent23/k04_cpython_k2496_n2_inverse.cpp), [Python original-source and planted-control test](../agents/agent23/k04_cpython_k2496_n2_inverse_sft.py), [manual CI matrix](../.github/workflows/h17-agent23-k2496-n2-inverse.yml). Original-source predecessor and its corrected wrap model: [Agent1](h17-k04-cpython-initializer-wrap-correction-20261106.md).
