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

## Portable single-file source and synthetic controls

The [read-only six-model causal-cut SFT](../agents/agent15/20261101_gap_causal_cut_sft.py) freezes all six source-index anchor tuples, verifies original spool SHA-256 and four incident-date job/time anchor identities, withholds selected row129 payload, checks both four-word hidden-gap inclusions per chronology, and independently evaluates thirty complete four-word predictions from five seeded CPython MT streams. The equivalent local script was run on the original uploaded ZIP and passed all thirty synthetic checks after an initial untemper inversion implementation error was corrected; the committed repository version has been reviewed but has not been independently run from a fresh checkout. This is a reproducibility aid for the *conditional donor location*, with no recovered original coupon.

## Stronger donor economy: one raw bit at the second gap controls one selected-coupon parity

The eight complete 32-bit missing draws above form a sufficient *full-coupon* donor set. There is a smaller and more exact **partial target-information requirement**. This observation holds in all six frozen model placements and uses a real intact original word.

Let `Y0` be the first 32-bit *tempered* printer payload word of the **authentic selected physical coupon**, read little-endian. Let `X` be the original hypothetical untempered MT state. In all six placements, source row43's final intact word is `X[p-624]`; actual source bytes `row43.word3=228BF401` untemper to **`59E4D0B9`**, with **bit31 = 0**. MT19937's twist constant `9908B0DF` has bit30 = 0, and a direct bitplane identity gives

```
X[p].bit30 = X[p-227].bit30 XOR X[p-624].bit31
           = X[p-227].bit30
Y0.bit30 XOR Y0.bit15 = X[p].bit30
```

The second equality uses the **actual source row43** (MSB zero), while the last comes from exact standard temper/untemper inversion: the mask of printed bits contributing to the untempered bit30 is `40008000` (printed bits 30 and 15). Consequently an **independently authenticated single bit30 of the one native draw `X[p-227]`**, located at **the fourth unprinted output after row96**, would determine one previously unknown **linear parity** of two bits of the authentic selected coupon. It does *not* determine either printed bit individually or the full coupon.

For the already-recorded incident route mask `8556C8CB...`, its little-endian first word is `CBC85685` and bit30 XOR bit15 = **1**. If this mask and selected physical print have separate integrity provenance, the corresponding *reduced* K04 first-word parity would equal `X[p-227].bit30 XOR 1`. These are strictly **conditional** original-bit relationships. The retained export does not supply or authenticate **that one generator bit** or the purported MT producer/state index, and the historical selected coupon remains unverified. **Actual K04 constrained original bits remain 0.**

Thirty independent source-free synthetic controls (five true Python MT seeds, all six p=950..955 positions) reproduced

```
((temper(X[p]) >> 30) XOR (temper(X[p]) >> 15)) & 1
 == ((X[p-227] >> 30) XOR (X[p-624] >> 31)) & 1
```

exactly, using the same corrected untemper/twist implementation as the full-word checks. This is a more discriminating potential *one-bit future witness* than an eight-fullword trace, but its historical source availability is still unproved. A metadata `CLASS` or `DEST` label without a source-certified mapping to **precisely `s96+7` and bit30** does not furnish it.

### Four-word parity extension: seven donor bits for four coupon parity equations

The single-bit identity extends directly across **all four** selected original output words `Y[j]=temper(X[p+j])`:

```
Y[j].bit30 XOR Y[j].bit15
    = X[p-227+j].bit30 XOR X[p-624+j].bit31,  j=0,1,2,3.
```

The `j=0` last term is the **known zero MSB of original row43.word3**. The other three MSBs reside in the unprinted first ordinary-job gap. Thus the *exact seven original witness bits* needed to fix these four selected-coupon two-bit parities in the six conditional models are: **four bit30 values of X[p-227..p-224]** from the second gap and **three MSBs of X[p-623..p-621]** from the first. No partial/categorical metadata source in the provided archive authenticates these seven exact full-draw bit positions. A successful independently indexed observation would give a four-equation parity constraint, with **124 other independent coupon dimensions potentially free even before other historical uncertainties**; it would not produce an accepted K04.

All **120** synthetic comparisons across five actual CPython MT streams, six p-index models and four selected words pass the original bitplane equation. This extends the earlier 30 first-word checks, using no selected H-17 original coupon bytes or acceptance hashes. The seven-bit count is a **sufficient partial-witness set** under the stated MT chronology and does not claim minimality under all possible auxiliary observations.

### One-bit future integrity discriminator for the disputed ACK copy

The **retained, unverified** selected row129 spool payload begins `A9A9DC57...`; its copied little-endian first word `57DCA9A9` has both bits30 and15 equal **1**, so the copied first-word XOR parity is **0**. Under the six-model MT identity above, an independently authenticated original bit30 of the **fourth native output after original job 0396** would equal the *true physical selected-coupon* first-word parity. Therefore, **if** the historical producer and draw index are separately established: observed donor bit **1** would definitively contradict the copied first-word parity, while observed donor bit **0** would leave only this one parity consistent and **would not establish overall coupon or route-mask integrity**. This conditional two-way test does not consult the K04 commitment, supply the donor bit or authenticate the producer. Never treat the current copied parity of 0 as an authentic missing generator-state bit.
