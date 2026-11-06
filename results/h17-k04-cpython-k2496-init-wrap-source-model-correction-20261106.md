# H-17 K04 CPython long-startup n2..4: a false-UNSAT wraparound trap

**Agent17, 6 November 2026.** This is a reproducible **solver correctness correction**, not a newly recovered component, original-source conclusion, or a claim that a historical Python printer producer exists. Original six REC8 components remain individually accepted, K04/K08 missing, combined incomplete.

## Affected model

The existing [Agent47 n2..4 SMT producer](../agents/agent47/k04_cpython_k2496_n234_source_smt.py) builds a necessary equation for the hypothesized CPython integer-key initialization after actual MT output origin k2496, assuming the speculative printer p951 chronology. Its default `include_s6=True` branch constructs `s1=(a1 XOR F2*mix(a623))-1`, then derives `s2..s6` by chaining from that `s1`. The original source-only model pins initialized `S6=E403BB7D`. Unfortunately, those are **not the actual CPython initialization dependencies**.

CPython `init_by_array` first seeds the 624-word `mt` register with `init_genrand(19650218)`. Its first loop runs **624 operations**. It updates registers 1 through 623, wraps to register1, and **updates register1 again**, using register623 and the final modulo-key index. After the wrap, the true predecessor for the second loop's first operation at index2 is the twice-written register1, `A1wrapped`. The second loop runs 623 operations from index2 through623, wrapping to index1 at the end. Accordingly, its *final* `S1` is produced after `S6`, and cannot be used to derive `S2`.

For unsigned 32-bit words, `mix(x)=x XOR (x>>30)`, `F1=1664525`, `F2=1566083941`, key length `n`, and the pre-wrap first-pass register `A`, the missing required step is

```
j = 623 % n
A1wrapped = ((A1 XOR (F1 * mix(A623))) + key[j] + j) mod 2^32
S2 = ((A2 XOR (F2 * mix(A1wrapped))) - 2) mod 2^32
S3 = ((A3 XOR (F2 * mix(S2))) - 3) mod 2^32
...
S6 = ((A6 XOR (F2 * mix(S5))) - 6) mod 2^32
```

The existing `controls()` also uses the stale-A1 version of `S1` and asserts it equals actual final `S1`, which is false on genuine Python-generated seeds.

## Independent genuine Python positives

Run [standalone stdlib SFT](../agents/agent17/k04_cpython_k2496_init_wrap_sft.py) against real `random.Random(seed).getstate()` reference words. All four synthetic seeds were produced using the true key-word integer-seed semantics and source-matched to genuine initialized register index6. The reported incorrect prediction deliberately uses the stale-A1/final-S1 model and genuine final S623, giving it *more* correct reference information than its symbolic form.

| Key words | Genuine initialized S6 | Corrected model S6 | Prior model S6 | Correct? |
| ---: | --- | --- | --- | --- |
| 1 | `D253A7B2` | `D253A7B2` | `7D08D0D5` | only corrected |
| 2 | `2681D359` | `2681D359` | `83005A7D` | only corrected |
| 3 | `27610DCD` | `27610DCD` | `89A8A00F` | only corrected |
| 4 | `AFD182E4` | `AFD182E4` | `4B26C5C5` | only corrected |

A second, independent local bit-vector test generated the identical first-pass and second-pass SMT formulas, fixed the seed words and each true initialized S6, and used Z3 QF_BV: **4/4 corrected SAT; 4/4 prior-model UNSAT**. The existing formula can therefore emit **false UNSAT** on authentic data. This is a mandatory correction before any future n2..4 contradiction can be interpreted as excluding the historical source. The synthetic controls do not establish the real source's seed.

## Original-source consequence and open attack

The retained spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, selected row129 withheld, projects 711 conditioned initialized-register bits at k2496, including `S6=E403BB7D` and `S7=1F7B301F` in the conditional p951 geometry, as previously reported by Agent28/47. Correct n2..4 inversion should combine those source bits with the **true wrapped first-pass** and second-pass dependencies. Solver model results need genuine Python-seeded controls; any putative original seed must replay all 132 intact printer packets before constructing selected K04, applying the unchanged route mask, and checking the original slot SHA256.

Preliminary source-only n2 SMT probes without this invalid S6 branch were satisfiable with only the earliest weak constraints and returned `UNKNOWN` for additional distant source constraints under short 20-second solver limits. **Neither a historical seed nor a K04 commitment match has been established.** The separate exhaustive one-word n1 result in [Agent47's report](h17-k04-cpython-k2496-oneword-complete-exclusion-20261106.md) derives from a distinct A7 inversion and is unaffected by this finding.

No original evidence, canonical candidate, acceptance or verifier was modified.
