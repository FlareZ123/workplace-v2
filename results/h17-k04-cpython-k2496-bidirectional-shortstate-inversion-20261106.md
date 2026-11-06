# K04 original CPython k2496: 17-step bidirectional initialized-state source inversion

**Agent17, 6 November 2026 | source-only conditional frontier.** This result creates a new *necessary* original-source seed test for CPython integer seeds of 2..4 32-bit key words at the speculative original printer p951 chronology and true CPython output offset k2496. It does not establish a physical coupon or recover K04. K01/K02/K03/K05/K06/K07 remain individually accepted, K04/K08 missing, combined incomplete.

## Why this changes the source inversion

The earlier [Agent47 long-startup n2..4 SMT generator](../agents/agent47/k04_cpython_k2496_n234_source_smt.py) attempted to constrain a known initialized S6 using the *incorrect* first-pass wrap/S1 predecessor. An authentic synthetic Python seed can be falsely UNSAT; see the [reproducible correction](h17-k04-cpython-k2496-init-wrap-source-model-correction-20261106.md) and [genuine seed controls](../agents/agent17/k04_cpython_k2496_init_wrap_sft.py).

A separate observation permits a shorter **sound necessary** source test without calculating first-pass register A623 at all. The previously established original printer source projection fixes initialized **S6=`E403BB7D`** exactly. CPython's second loop updates indices2..623 sequentially using

```text
S[i] = (A[i] XOR (1566083941 * (S[i-1] XOR (S[i-1] >> 30)))) - i (mod 2^32)
```

Because 1566083941 is odd, it has a multiplicative inverse modulo 2^32. The transform `x XOR (x >> 30)` is also self-inverse on 32bit words. Therefore for i=6,5,4,3,

```text
S[i-1] = unmix(INV_F2 * (A[i] XOR (S[i] + i))) (mod 2^32)
```

where `A[i]` are first-pass words computed from just the first **17** CPython seeding steps. Reverse the known S6 to calculate S5..S2, and advance from that same S6 to S7..S17. The true final initialized **S1 is excluded** from this reverse test: CPython writes it at the end of its second pass; it was not the predecessor used when computing S2. Thus this method respects the actual wrap dependency while avoiding a full 624-step bitvector expression as a *necessary* early filter.

## Eight source-pinned observations

The original 132 intact printer packets (selected row129 withheld) at real output origin k2496 have rank15,365 in the p951 hypothesis. A local independent reproduction of the [Agent28 initialized-register projector](../agents/agent28/k04_cpython_real_output_offset_sft.py) recovered **711** fixed initialized-register bits, including these eight chosen masked words:

| Index | Fixed mask | Expected source bits | Purpose |
| ---: | --- | --- | --- |
| S2 | `09CC1C00` | `00C40000` | backwards |
| S5 | `8000001F` | `00000011` | backwards |
| S6 | `FFFFFFFF` | `E403BB7D` | 32-bit anchor |
| S7 | `FFFFFFFF` | `1F7B301F` | forward |
| S8 | `09CC1C00` | `008C1000` | forward |
| S15 | `000000FF` | `000000B6` | forward |
| S16 | `5398BA7D` | `4010A820` | forward |
| S17 | `01800800` | `00000800` | forward |

The seven comparisons outside the 32-bit S6 anchor account for **85 source-fixed bits** (some may be statistically dependent). The source original spool SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Mask projections were checked against the independently recomputed source-derived state array. The selected physical/copy ACK2 bytes, K04 mask, K04 target, verifier and K08 are not used.

## Reproducibility and actual results

The [standalone SFT and SMT generator](../agents/agent17/k04_cpython_k2496_bidirectional_sft.py) computes genuine Python integer-seed initialized registers, source-normalizes the eight masked values, and tests both forward and backward constraints. **All three genuine seed lengths n2,n3,n4 PASS**, and a deliberately flipped authentic source bit is rejected for all three. Separately constructing the generated SMT with all corresponding actual seed words fixed yields **SAT in Z3 for 3/3 genuine lengths**. A random n2 candidate fails the original source projection as expected.

Local Z3 on the *unfixed original n2* source expression was **UNKNOWN after 30 seconds**, as were two alternative standard QF_BV tactics after 15 seconds each. None is evidence of satisfiability or unsatisfiability. A stronger [manual-only Bitwuzla 0.9.1 job](https://github.com/FlareZ123/workplace-v2/actions/runs/42301480409) began at 22:01 UTC, currently in the actual original-source solve step, bounded to 1,200 seconds. It has already passed checkout and installation. Treat its final result according to its logs, not its status alone.

If a 2-word original-source model reports **UNSAT**, the exact CPython k2496/p951 64-bit integer seed family is excluded by these necessary constraints. If **SAT**, the model key is merely a provisional seed and must replay all 132 intact printer packets using actual CPython initialization and actual 2,496 preceding draws, *before* generating any selected coupon and testing original acceptance. The 17-step source test alone does not certify a K04 candidate.

No original evidence, canonical candidate, acceptance or verifier changed.
