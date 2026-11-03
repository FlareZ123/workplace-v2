# K04: 164 newly source-consistent printer chronologies produce 571 new full component candidates

**Agent 44, 3 November 2026. Original K04 result: zero matches among 1,516 distinct complete candidate values.** K04 authentic original coupon bits remain unknown; Emily's K08 exact final caption is also absent. The six previously accepted slots remain untouched, and combined REC8/1 remains INCOMPLETE.

## New cracking mechanism

The original [six-geometry complete hidden-stage scan](h17-k04-p951-hidden-stage-source-derived-coupon-scan-20261103.md) assigned preserved printer payloads to six specific source-compatible, historically unconfirmed MT19937 output chronologies p950..955, generating 945 distinct complete masked component values. Those six are **examples** from a much larger family of source-consistent timings. A different original timing might fully reveal another *unprinted* 16-byte generator buffer that generated the disputed 18:02 ESC-N attempt2 physical coupon before its damaged archive copy was made.

This experiment searches **new source-consistent chronologies**, then uses the original source state to construct complete four-output candidate values at alternate issuance stages. It requires no partial SHA256 target guesses, copied selected ACK2 bits, additional K04 component material or arbitrary 32-bit brute force.

### Exact finite method

1. Start with original SHA256-pinned source `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Parse 132 intact original print payload rows and **skip selected row129 before reading its hex**. Interpret four 32-bit little-endian output words per row, inverse MT19937 tempering.
2. Use the 25 original full three-word recurrence witnesses, 17 boundary witnesses and the independent adjacent two-step quartet connecting rows9/40/63/124. Those equalities partition the 133 source row-start positions into **81 connected stream-index root components**.
3. For each of six source-compatible original chronology fixtures p950..955, change **exactly one root component** by −2, −1, +1 or +2 output draws. All associated source row offsets move together. Require row0 origin zero, selected row129 position fixed, strict chronological ordering with the published ordinary/tail draw floors, and the original row130→131 four-draw adjacency.
4. Reject source-inconsistent placements first through complete known threeword MT recurrences, then through **the entire 132-row source GF(2) state system**, including every intact original 32-bit word. Compute the 128-dimensional selected target quotient for every surviving placement. All original data remain read-only.
5. Under every surviving placement, inspect every native four-successive-output window from stream start to the final preserved spool row. If the intact source fixes all 128 bits or leaves exactly one bit unresolved, enumerate its **complete** 16-byte coupons (one or two assignments), temper and serialize as printer bytes, XOR the unchanged route mask, SHA256 the full masked component and compare to the original K04 commitment. Deduplicate complete component bytes *across* placements.

This is an alternative generation-stage hypothesis. The source does **not** authenticate any hypothesized stage as the selected 18:02 physical ACK2 coupon, and the published six chronologies have independent metadata-producer contradictions. The test measures only the specified coherent linear source/timing models.

## Exact original-source outcome

| Nominal selected output stage | Chronologically eligible one-root shifts | All-source GF(2)-consistent shifts | Distinct complete components including baseline |
| ---: | ---: | ---: | ---: |
| 950 | 104 | 34 | 578 |
| 951 | 103 | 27 | 528 |
| 952 | 89 | 24 | 556 |
| 953 | 89 | 20 | 505 |
| 954 | 93 | 30 | 581 |
| 955 | 79 | 29 | 575 |
| **Total** | **557** | **164** | **1,516 overall distinct** |

The last column is **a set union**, so its per-model values must not be added to obtain the overall number. The 164 valid shifted placements produce **571 new distinct complete component values** beyond the earlier six-model union of 945. All **1,516** distinct source-generated complete component values are rejected by the **original unchanged K04 SHA256 commitment**; no physical coupon or masked component passes.

Every shifted chronology's source-based selected target quotient remains exactly **128 unknown bits out of 128**. In particular, source compatibility of a new chronology does not imply any authentic selected-output bit was recovered. A committed local Python positive control plants the SHA256 commitment of one enumerated 16-byte component and recovers it exactly once, guarding the complete coupon/commitment path.

## Reproduction and limits

Pure standard-library SFT: [single-root perturbation reproducer](../agents/agent44/k04_single_root_perturbations_sft.py). It imports the two previously source-controlled [six-geometry](../agents/agent44/k04_six_stage_sft.py) and [p951](../agents/agent44/k04_p951_hidden_stage_coupon_sft.py) test modules, uses the frozen 81-component labels derived from original recurrence witnesses and asserts every row count, target quotient, all 1,516 distinct candidate values, zero authentic matches, and planted positive. A separate locally executed implementation that **regenerates the 81 groups directly from the 25+17 source witnesses** produced the identical outputs and planted positive in 36.7 seconds; the shorter committed portable version was remotely readback-verified. The retained event case, route, mask, acceptance file, candidate file, and verifier were not changed.

The numerical shifts ±1/±2 explore local source-compatible variants, not every possible chronology or remote printer producer. A 16-byte alternate-stage scan remains historically speculative without the original **target event's generation/capture/copy witness**. None of these cleanly reconstructed other-stage buffers is certified as the missing selected physical coupon. The 164 negative cases supply no K08 caption words. The appropriate next advance must causally link a selected-event stage or surviving independent original coupon, or recover the author's actual final caption.
