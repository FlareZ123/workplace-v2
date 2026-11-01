# K04: two ordinary print-job gaps cover the missing target ancestry in all six source-consistent cross-stream MT geometries

**Agent 15, 1 November 2026. Conditional source-to-target acquisition result.** The original six known REC8 slots stay PASS. K04 original selected coupon **0/128 authenticated bits**, K08 final caption **zero attested words**, combined **INCOMPLETE**. This report reconstructs **where a genuinely new independent generator-state witness would have to reach**; it does not claim the hypothesized producer or the missing state actually survives.

## Original observations and existing exact models

Use original SHA-256-pinned `evidence/print/spool-reconstruction.log` (`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`). Routine printer row43 is `PS-261003-0343` at **10:35 UTC** and row44 is `PS-261003-0344` at **10:40 UTC**. Row96 is `PS-261003-0396` at **15:00 UTC**, followed by row97 `PS-261003-0397` at **15:05 UTC**. All four rows have intact retained 16-byte payload fields. The selected disputed 18:02 UTC ACK2 is row129.

The independent published model file `workplace-v1/agents/agent5/k04_crosssource_six_vectors.json` contains six *fully printer-source-consistent* conditional MT19937 output-index assignments, one for each selected start `p=950..955`. Those geometries also obey the previously published TRP2/withdrawn RC-17 recurrence-offset constraints; their **historical single-generator producer and consumption chronology remain unauthenticated**. This analysis reads all six original source-only indexed vectors, performs direct integer comparisons, and does **not** use the selected row payload, original route mask, K04/K08 commitments or final phrase to select geometry.

## Six-way invariant causal cut

For each model, let `s[r]` be original printer row `r`'s hypothetical MT output start. All six have the same exact relative alignments:

```
s[43] = p - 627      s[44] = p - 616
s[96] = p - 234      s[97] = p - 222
s[129] = p
```

Hence row43's last untempered payload word is `X[p-624]`; the next four words `X[p-623..p-620]` fall entirely in the **unobserved 10:35→10:40 gap** before row44. The four words `X[p-227..p-224]` fall entirely in the **unobserved 15:00→15:05 gap** after row96 and before row97. Both classifications hold for **all six existing cross-stream-compatible examples**, despite their different absolute selected start positions:

| Selected p | Known first predecessor | Four missing early words | Four missing middle words | Source job boundaries |
|---:|---|---|---|---|
| 950 | X326 = row43 word3 | X327..330 | X723..726 | 0343→0344, 0396→0397 |
| 951 | X327 = row43 word3 | X328..331 | X724..727 | same |
| 952 | X328 = row43 word3 | X329..332 | X725..728 | same |
| 953 | X329 = row43 word3 | X330..333 | X726..729 | same |
| 954 | X330 = row43 word3 | X331..334 | X727..730 | same |
| 955 | X331 = row43 word3 | X332..335 | X728..731 | same |

The exact MT19937 recurrence for `j=0,1,2,3` is:

```
X[p+j] = X[p-227+j] XOR twist(X[p-624+j], X[p-623+j])
```

For the first input word `X[p-624]`, the intact row43 supplies its full bits. **Therefore eight newly authenticated complete 32-bit state/draw words**, the two indicated four-word gap families, suffice in each conditional model to calculate *all four* untempered selected words. Temper these four results and serialize in original printer little-endian format to obtain the full hypothetical 16-byte selected coupon; use the existing independently authenticated mask only after producer, chronology and copy integrity are established. The eight-word set is a concrete **sufficient donor set**, not a mathematically minimal one.

Synthetic validation: five independent CPython MT19937 seeds (0,17,20261003,314159,0xC0FFEE) passed all four equations at selected output indices955..958, using corrected standard inverse-tempering. No original selected bytes or acceptance hashes were consulted in that control.

## Acquisition and stopping decision

A truly **historically indexed native printer trace or preserved generator-state snapshot** exposing full draws in both ordinary-job intervals could provide a *target-reaching alternative* to physically recovering the 18:02 coupon. This report does not establish that such detailed printer traces exist, that CLASS/DEST labels reveal those words, or that a single MT19937 stream generated physically separate equipment. Existing source metadata provides **zero** of the eight additional full words. Both the original 128-bit conditional target quotient and the unresolved physical coupon/mask integrity remain decisive.

The invariant is proved **across the six published source-compatible example geometries**, not over every possible printer chronology or alternative generator. The printer-only p955 vector happens to share this job-gap map; it is independently inconsistent with some cross-stream offsets and must not be conflated with the six-model witness set. No new target values were guessed, and no K04/K08 acceptance test was performed. Do not turn this result into a new blind PRNG family, speculative source-census or broad CI sweep absent an independently sourced draw trace or historically authenticated producer.
