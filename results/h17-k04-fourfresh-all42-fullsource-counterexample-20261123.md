# H-17 K04: a genuinely source-consistent four-fresh-output printer chronology exists

**Agent 10 | 23 November 2026 | Constructive entire-original-source counterexample. K04 remains MISSING.**

## What this resolves

The 23 November all-42 stage-vector report showed an exact original-source MT19937 fit with a selected printer stage at 952, but its 18:01 REQUESTED packet advanced only one native output before the selected 18:02 ACK. Such overlap may not describe real physical print emission. Agent1 subsequently sampled three schedules in which every printer packet consumed at least four distinct consecutive outputs. All three contradicted the actual full original source; that finite sample was explicitly **not an exhaustive exclusion**.

We tested the stronger question: **Can any nearby chronology satisfy all 42 original MT recurrence witnesses, treat every historical printer row as a fresh four-native-word output buffer, and still reproduce every source word?** Yes. The constructive answer weakens any argument that overlap or duplicate printer buffer consumption is mathematically necessary to explain the observed MT-style source.

## How the complete counterexample was found

Using the exact original 132 intact spool payloads, omit row129, PS-261003-0417 attempt2 ACK, **before any copied PAYLOAD decoding**. Preserve all 84 original source-derived stage-difference equations from 25 fullword and 17 partial MT recurrence witnesses. Solve a small integer-gap model:

- packet start gap **4..16 native words** for every historical row, including REQUESTED rows;
- the first PS-0417 REQUESTED buffer at row128 must precede selected ACK2 by **at least four** draws;
- the selected ACK2 must precede the third REQUESTED row130 by **at least four** draws;
- minimize total absolute deviation from Agent11's frozen source-consistent schedule.

The minimum attainable L1 gap change is **20 native draws**. We sampled 200 slightly reweighted integer-optimal models, obtaining 192 distinct schedules. Eleven of these independently passed the **entire 528-word original source GF(2) consistency test** (source rank 15,433 to 15,435). This is a finite constructive search, not a census of all 4-fresh compatible schedules.

One frozen compatible schedule has these ten exact gap changes relative to Agent11's 133-row vector:

| Gap after original row | Change (native draws) |
| --- | ---: |
| 12 | +2 |
| 25 | −2 |
| 43 | +2 |
| 47 | −2 |
| 66 | +2 |
| 79 | −2 |
| 96 | +2 |
| 109 | −2 |
| 128 | +3 |
| 129 | −1 |

All resulting 132 consecutive gaps are **4..13**, with row128 start **951**, the missing selected ACK row129 start **955**, and row130 start **959**. Every original 42 numerical source relation remains satisfied. The entire 528 intact native 32-bit observations produce **zero contradictory GF(2) equations**, source rank **15,434**.

## Strong full-state demonstration

The [source-pinned single-file test](../agents/agent10/k04_all42_fourfresh_countermodel_sft.py) constructs a complete 19,968-bit initial MT generator state by solving the source linear system, assigning unused state coordinates zero. Every one of the 528 retained original native words is recomputed **exactly**. The selected stage955 four-word packet projects to **128 independent remaining bits**: no original printer payload fixes a single target degree of freedom.

It then toggles an independently free initial-state bit, resolves the exact same source equations again and obtains a *second* complete MT state. The two states independently reproduce **all 528 original intact words without a single difference**, yet emit different complete selected printer packets:

- **Synthetic state A selected payload**: 00000000000000000000000000000000.
- **Synthetic state B selected payload**: 91004000000000000000000000000000.

These are **model witnesses, not historical coupon claims**. Their purpose is to demonstrate source-compatible ambiguity with explicit bytes at every stage. The original selected copied ACK2 payload, official K04 acceptance hash and recovery candidate are not inputs to the source-state fitting. The original read-only SFT ran successfully against the supplied ZIP's extracted official files.

## Consequence for actual recovery

The full original spool can be **exactly** consistent with a standard four-fresh-outputs-per-packet MT chronology, without any packet overlap. This chronology leaves the selected coupon's entire **128-bit value unobserved**. The commitment still supplies a test for a complete candidate, but a direct 2^128 source-state search is not a practical reconstruction method. The selected historical stage and actual printer MT generator also remain unauthenticated.

This closes the narrow objection that no 4-fresh source fit can exist. Further recovery needs a separate source-authored emitter, a target-linked print/media witness or a strong cross-record constraint that predicts a **complete** physical K04 coupon. The existence of compatible states alone cannot furnish K04. K08's final keeper phrase remains missing. Official combined REC8/1 is still INCOMPLETE; source, route, verifier, acceptance and canonical six-slot candidate are unchanged.

**Related:** [all42 first source-compatible chronology](h17-k04-all42-full-source-alternative-chronology-20261123.md); [four-fresh sampled negative control](../agents/agent1/k04_all42_fresh_four_output_sft.py); [286 additional whole-coupon candidates and original checks](h17-k04-all42-whole-stage-window-coupon-20261123.md).
