# K04: original K02 and K05 close-in-time cross-record stage falsifier

**Agent 34, 4 November 2026.** This is a genuinely distinct conditional source-to-source test at the *two late future MT donor stages* recently nominated by Agent 1. **No K04 value recovered, no K08 words recovered.** The original six accepted components and official verifier/commitments remain unchanged.

## New hypothesis and why it matters

Agent 1 showed that the eight **selected original** K02 GOOD/HOLD `LT-204/DIAG_WORD` halfwords could be interpreted, under a hypothetical common MT19937 producer, as four full consecutive 32-bit donor words at native stages **1178 or 1405**. Each placement conditionally removes 95/128 of the target native-stage uncertainty, yielding 16 disjoint 33-bit candidate cosets per stage. The model's causal link from the telemetry to the printer is speculative.

A previously under-tested independent original source is the **K05 selected** node49/event82 recorder group, sequences 300..303, four complete CRC-good 4-byte controls taken at 21:14:00–21:14:07. These immediately follow K02's 21:13:40–21:13:47 selected freeze, separated by ~13 seconds. Agent 6's new recorder lattice found older and alternative K05 groups matching source-fixed *negative* native stages, whereas the **actual selected seq300..303** failed in its scanned negative-to-1040 window. The new positive future stages 1178 and 1405 were not the subject of that negative-stage scan.

**New discriminator:** if K02 and K05 are a shared *consecutive* printer MT output stream with a small time-proportional intervening draw count, adding the four selected K02 words at stage 1178/1405 may predict informative bits of the four selected K05 words at a nearby later stage. This tests the specific source-to-source emitter hypothesis before assuming either record reveals the missing 18:02 K04 physical ACK.

## Frozen original observations and mechanism

- Original K02 selected eight 16-bit values (big-endian source reducer bytes): `E1A5 E474 BAD7 E853 A2E8 C71D 3317 D507`. Original telemetry source SHA256 `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`.
- Original K05 selected CRC-good node49/event82/latches0..3 seq300..303 raw four words: `FF8B7820 0A56E858 6DCDA00E F01E4572`. Recorder source SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`.
- Original printer p951 symbolic closure of the other **132 actual** spool packets: GF(2) rank15365. The selected printer row129 is excluded from source fitting and no K04 hash or selected copied bytes enter the test.
- For each K02 donor stage 1178/1405, 16 natural interpretations (word endian, reverse four-word order, flip halfword order within each word, native-vs-tempered) yield independent rank128 additions. Then K05 is placed contiguously at each offset **4..44 native MT words after the K02 donor**, each under eight interpretations (endian, four-word reversal, native-vs-tempered). Predictions are checked only where the extended source basis fixes the corresponding K05 output bit.
- Total `2 × 16 × 41 × 8 = 10,496` full-source hypotheses. Any pair with 16 or more independently predictable K05 bits must match **all** predictable bits to count as a positive. This does not rank partial target hashes.

## Executed original-source results

| K02 donor stage | Complete assignments | With >=16 predicted K05 bits | Exact informative matches | Max predicted bits | Fewest mismatches for >=96 predicted bits |
|---|---:|---:|---:|---:|---:|
| 1178 | 5,248 | 4,992 | **0** | 128 | 38 |
| 1405 | 5,248 | 4,992 | **0** | 128 | 41 |
| **Total** | **10,496** | **9,984** | **0** | 128 | |

At stage1178+7, one interpretation gives all **128** K05 bits predetermined and **55** differ from the original selected K05 bytes. At stage1405+6, an all-128-bit prediction differs in **56** bits. Therefore the selected K05 quartet is strongly inconsistent with several close-contiguous emitter placements even though each K02 donor stage alone is source-compatible.

**Controls:** a full 19,968-bit state constructed from original spool and K02 stage1178 constraints produces a synthetic four-word K05 row at stage1185 which matches 128/128 predicted bits; flipping one bit produces exactly one detected discrepancy. Source SHA pins and CRC-good selected-K05 extraction assertions pass. The complete read-only source SFT is [here](../agents/agent34/k04_k02_k05_cotemporal_stage_sft.py); it uses the pre-existing [symbolic model](../agents/agent49/k04_p951_symbolic_basis.py).

## Interpretation and next experiment

The K02 raw-donor stages **1178/1405 cannot be promoted to a common near-time K02→K05 emitter at offsets 4..44** with any of these natural word presentations, provided one insists on all original fixed bits. In particular, the adjacent chronology alone is insufficient to select a particular K02 donor stage or eliminate K04's residual 33-bit coset.

This falsifier does **not** invalidate either complete K04 coset computation as a mathematical conditional candidate family: K02 and K05 may have independent producers, the source record times may be separate from generator output times, the gap may be larger, the stage may be different, and the K05 four-word grouping may use a different transform. The actual selected 18:02 ACK2 print media remains unauthenticated; the original source provides no shared-generator declaration. This is a precise, useful historical-stage warning, **not** a seventh-slot recovery.

Continue seeking a source-grounded stage/role explanation that predicts a complete heldout *original* source object, and an exact terminal K08 caption. Avoid another blind K02-phrase or arbitrary stage-coset sweep without new discriminating structure.


## 4 November follow-on: interleaved individual K05 writer words, +4..+96

The initial test required all four selected K05 latches to be emitted as a *contiguous* four-word printer-generator block. A second, materially different chronology hypothesis allows independent intervening draws between each 1Hz selected K05 latch; its necessary condition is that **each individual selected 32-bit K05 word** can occur *somewhere* after the four K02 donor words and before stage+96.

Source-only screening expanded the same two K02 donor-stage families, sixteen K02 input presentations and both native/tempered K05 word interpretations; for every source-selected K05 latch 0..3, it looked at every stage+4..+96, with both within-word byte endiannesses. This is an **individual word** screen. If no single latch can match in any informative position, no monotone four-latch interleaved schedule exists in that range. Predictions counted only when >=16 of a candidate word's 32 bits are independently fixed by the other original source fields.

| K02 donor stage | Informative individual K05-word assignments | Full fixed-bit matches | Minimum mismatching fixed bits |
| --- | ---: | ---: | ---: |
| 1178 | 11,520 | **0** | 7 |
| 1405 | 11,008 | **0** | 7 |
| **Combined** | **22,528** | **0** | |

All four actual K05 selected words fail to produce **even one** informative full-word match at any tested future stage under this conditional producer. A planted source-constrained output at stage1185 matches all 32 fixed bits; flipping one bit produces exactly one discrepancy. The [existing SFT](../agents/agent34/k04_k02_k05_cotemporal_stage_sft.py) was extended to reproduce these counts, keeping the source/commitment separation.

The extension refutes all informative monotone/interleaved schedules in this *finite future interval* under the two hypothetical donors, but remains unable to rule out a more distant epoch, an independent recorder producer or a different non-wordwise transform. No actual physical K04 coupon or K08 final text is thereby recovered.
