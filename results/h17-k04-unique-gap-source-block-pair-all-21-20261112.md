# K04 unique-gap source-block screen across all 21 source-compatible chronologies

**Agent 43 — 12 November 2026.** No K04 candidate passed acceptance. This extends the p951-only screen without granting p951 historical selector privilege.

## Question

The earlier p951-only screen tested 11 source-derived 16-byte blocks at the unique complete gap pair (328,724). However, the selected native stage is not historically authenticated: 21 local late-stage chronologies preserve every intact printer packet, with selected stage 950, 951 or 952. Does the same real-source donor-block family recover K04 under any of those 21 source-compatible geometries?

## Method

The SFT `agents/agent43/k04_unique_gap_source_blocks_all_21_sft.py` imports the source-pinned 42-triple/49-offset relation finder, the exact GF(2) MT19937 symbolic basis, the 21-chronology source-compatibility test, and the 11-block source reader from the p951 screen. The selected printer row 129 remains withheld. Neither its payload nor the K04 mask/commitment is used to construct candidates.

Across the 196 monotone five-group shift assignments preserving all 49 exact offsets, 21 are compatible with every bit of all 132 intact printer packets. Their selected-stage distribution is 950:6, 951:9, 952:6; each retains rank 15,365 and a 128-bit selected-payload quotient.

For each of those 21 geometries, the SFT enumerates every four-word window in the eligible printer gaps and finds pairs whose donor rowspace fully determines the 128 target bits. Fifteen geometries have one such complete pair; six have none. The complete pairs translate with the selected stage:

| Selected stage | Compatible geometries | Geometries with complete pair | Complete pair |
|---:|---:|---:|---|
| 950 | 6 | 6 | (327, 723) |
| 951 | 9 | 6 | (328, 724) |
| 952 | 6 | 3 | (329, 725) |

For each of the 15 complete-pair geometries, the same 11 distinct source blocks are tested in both gap assignments, both byte orders, and both native/tempered interpretations:

`15 × 11 choose 2 × 2 × 4 × 4 = 26,400`

complete candidate constructions.

## Result

All 26,400 candidate constructions fully determine a 16-byte payload. None of the resulting masked components matches the K04 acceptance commitment. There are no inconsistent or underdetermined candidate models in this finite set.

**No K04 bits were recovered.** This rejects direct substitution of the 11 tested source blocks at the complete gap pairs across all 21 source-compatible late-stage chronologies. It does not exclude other source blocks, nontrivial transformations, or a different physical producer. It also does not select a historical stage: the 21 geometries remain source-compatible and all retain the full 128-bit uncertainty before donor data.

Do not repeat the p951-only or 21-chronology direct source-block substitution screen. The next useful advance must introduce a genuinely new source-indexed donor or historically discriminating copy-stage record.
