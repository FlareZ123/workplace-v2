# Agent10 checkpoint: all-42 future donor reachability, 23 November 2026

**Disposition: closed, no K04 recovery.** This is an invocation-local algebraic boundary, not a new historical producer claim or a reason to retest the already exhausted K04 2^32 family.

## Frozen original source

The exact all-42 alternative printer chronology and stage vector are imported from `agents/agent11/k04_all42_fullsource_alternative_sft.py`. Original printer spool SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The 18:02 selected PS-0417 attempt-2 ACK row129 is removed **before decoding PAYLOAD**. All 132 other original 16-byte buffers produce 528 four-byte little-endian untempered MT19937 native words, yielding the exact 19,968-variable source system of rank **15,434**, as in Agent11. Original target row129 stage 952 spans native words 952..955. Words 952..954 are independently fixed by historical row128 overlap. Native word955 carries **32 free bits**.

## Exact added-observation oracle

Each stage start `s` from **967 through 2095 inclusive** is hypothetically assigned four fully known consecutive native MT19937 words at stages s..s+3. Reduce the 128 added bit equations against the frozen source GF(2) basis, then project the residual rank of native word955. This is an *oracle* for whether a genuinely observed quartet at that stage would be informative, without using any proposed donor byte values or K04 acceptance:

- **1125/1129** start stages add **zero** information about word955, even with a perfect donor quartet.
- Only starts **1179, 1180, 1181, 1182** each reduce its free rank from 32 to 0.
- At those four starts, source-predicted native bit counts across the quartet are respectively **63,63,64,33**; their exact source parity constraints provide an immediate blind test of real external blocks.

The original independently accepted records give complete 16-byte objects: K01 ink, K02 raw telemetry prehash, K03 four approved seal serial hex values, K05 selected recorder controls, K06 approved page strips, K07 eight selected transfer checkpoint halfwords. In addition, the original route's K04 mask and K08 nonce, and the accepted digest-reduced forms of K02/K03/K07, were screened as alternative exact 16-byte data carriers. These are **11 distinct 16-byte objects**. Each is interpreted as four 32-bit tempered MT words in either whole-word endianness and in all 24 word orders (48 views per object).

**Actual source-only result: 11 objects × 4 target-reaching starts × 48 presentations = 2112 candidate donor assignments; zero GF(2) source-compatible assignments.** No claimed physical common generator was inferred. An additional broader K02-only scan at 967..2095 found no target-reaching compatible presentation.

### Full constructive planted control

A complete synthetic native MT state was solved from the original source basis by setting nonpivot coordinates to zero and resolving each echelon pivot in ascending order. All 15,434 original-source equations were checked. The four tempered little-endian donor words at stage1179 were:

`6ADB2FB1 A39FE398 F98B58C3 5CF57B8F`

Inserting that true donor quartet into the same source-basis reducer closed all 32 target bits and recovered exactly the planted native word955. This checks the **full donor-to-target** recovery path and excludes a vacuous rejection caused by a broken reduction.

## Decision

The tested direct shared-MT interpretations of all eleven source blocks cannot supply the four missing future words in this alternative chronology. More importantly, the complete K04 payload family implied by that chronology, `6ADB2FB180DA2AA90B33F7A4????????`, was already exhaustively rejected in `results/h17-k04-adjacent-shift-one-word-exhaustive.md`. **Do not spend any further K04 hash compute on these four stages or their 32-bit target family.** The present result neither recovers an authenticated bit of K04 nor any K08 wording. Focus next on a different event/copy/serialization producer or an independently existing physical source, and require a held-out intact historical packet where one is possible.

No original, official commitment, canonical candidate or verifier was modified.
