# K04: 399 complete alternate-generation-stage coupons reconstructed from intact printer data

**Agent 44, 3 November 2026.** This experiment creates complete K04 candidate values from source-derived *unprinted* and cross-boundary MT19937 outputs, under the published conditional p951 chronology. **No K04 candidate passed** the original unchanged commitment. Six pre-existing verified slots remain PASS; K04 and K08 remain missing.

## New target-facing interpretation

The prescribed K04 source is the 18:02 UTC ESC-N attempt-2 ACK coupon, but the original printer export preserves dispatch state separately from copied media bytes. As an exploratory alternative, the physical coupon might have been *generated or queued at a different output stage* from the recorded ACK. In the conditional p951 single-MT stream, an earlier or differently framed four-output window can sometimes be recovered fully from the **132 other intact print rows**, including four-output windows containing unprinted metadata draws or crossing two ordinary jobs.

The question tested here: **Does any source-determined four-consecutive-output window with at most one residual native-state bit produce the committed K04 component when XORed with the source-prescribed mask?** This differs from Agent21's [four selected-adjacent shifted-stage 32-bit brute-force families](h17-k04-adjacent-shift-one-word-exhaustive.md): it extracts conditional state values at *every* stage from the full source GF(2) system, without restricting to slices of the copied target or three intact adjacent source bytes. This is a bounded alternative generation-stage search, not a source-authenticated record of when the selected coupon was generated.

## Source and model

- Original printer log SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Freeze the source-compatible p951 vector from the original Agent5 [six chronology examples](https://github.com/FlareZ123/workplace-v1/blob/main/agents/agent5/k04_crosssource_six_vectors.json). These geometries are historically unconfirmed and the exact immediate CLASS/DEST sampler is independently contradicted by intact source in [the two-witness producer test](h17-k04-six-fixture-dest-only-two-witness-cut.md).
- **Erase original selected row129 before building any equations.** Each other 16-byte spool payload supplies four little-endian MT-output words. Invert MT tempering and build affine state equations over 624 initial 32-bit words. The real source rank is **15,365**, without contradictions in this hypothetical geometry.
- For each native output position 0..966, reduce its 32 bit-expressions against the source basis. For every four-output window beginning at position 0..963, enumerate its exact native completions **only if at most one bit is unresolved**, temper the four words, serialize little-endian, XOR the source K04 mask, and compare the resulting 16 bytes to the untouched original SHA256 commitment.

This process uses no selected attempt-2 copy to infer source bits or choose stream indices; the official hash is consulted solely after complete candidate construction.

## Executed source result

| Observation | Exact count |
| --- | ---: |
| Source-consistent affine rank | **15,365** |
| Four-output windows fully known | **253** |
| Four-output windows with exactly one unknown bit | **73** |
| Complete 16-byte coupon candidates tested | **399** |
| Original K04 SHA256 matches | **0** |

Of those 399 assignments, 253 come from fully source-fixed windows and the other 146 exhaust both branches of each 1-bit window. They include ordinary-record slices, cross-boundary windows, and **genuinely unprinted** outputs. An illustrative four-output unprinted window begins at output index **697**, between original row93 (14:45) and row94 (14:50). Its fully reconstructed, unrecorded 16-byte stream is `C9304FE833674EFD67B213839E4BA01D`. Its inferred four 32-bit outputs encode **DEST rejection 3, rejection 3, acceptance bench 2, then next CLASS acceptance LABEL 0**, agreeing retrospectively with the two original metadata labels. Such a local alignment is supporting evidence for the specific model's local state reconstruction; it does not fix the model's contradictions elsewhere or prove an event-specific coupon lineage.

A more event-adjacent example is stage **888** after the 16:50 ordinary spool row118, following the earlier same-numbered row117 print at 16:45. This four-output window has exactly **one** unknown native bit and therefore **two** complete coupons. Neither matches the selected K04 commitment. No source states that the 18:02 physical ACK2 coupon was precomputed at stage888; the example only makes the alternate-stage hypothesis reproducible.

## Positive controls and reproduction

The [self-contained original-source SFT](../agents/agent44/k04_p951_hidden_stage_coupon_sft.py) asserts printer SHA, MT temper/untemper round-trips, exact source rank, the four recovered row93→94 hidden outputs and their original CLASS/DEST labels, all candidate cardinalities and a **planted commitment for precisely one of the two distinct stage888 branches**. These checks passed in local Python 3 against the unchanged uploaded original 46-member archive extracted into a read-only fixture. Script source was committed by GitHub contents API and verified by remote readback; no CI execution is claimed.

## Scope and next crack

This scan eliminates **only** the 399 completed alternate-stage hypotheses from this single p951 source geometry. No originally certified generation index, source-state transfer, printer dispatch/copy transformation, or physical ACK2 coupon was identified. The p951 historical producer premise remains contradicted by other original metadata witnesses, and a different chronology could alter the predicted windows. Stage windows containing 31 or more free bits were intentionally excluded because their unanchored enumeration would be vastly more costly. Those candidates are neither recovered nor excluded.

The original K04 physical selected coupon remains **0/128 authenticated bits**; the exact K08 terminal caption remains **zero authenticated words**. No accepted eighth-slot or combined REC8 key is claimed. A high-value next step is an independently evidenced *event-specific* generation-stage or original copy-integrity witness that links the selected 18:02 ACK2 to a distinguishable generated-output window, rather than unboundedly expanding a source-compatible stage scan.

## Six-chronology extension, 3 November ~23:15 UTC

A second read-only test generalizes the same source-derived complete-coupon architecture to **all six published original-source-compatible p950..955 row-start vectors**, rather than choosing only p951. The selected physical ACK2 remains excluded from every source equation. Every scenario's complete state-consistent source rank and full/one-bit window counts were checked independently.

| Conditional selected start | Original source rank | Fully known fourword windows | One-free-bit windows | Complete coupon assignments | Original K04 matches |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 950 | 15,366 | 244 | 67 | 378 | 0 |
| 951 | 15,365 | 253 | 73 | 399 | 0 |
| 952 | 15,367 | 264 | 84 | 432 | 0 |
| 953 | 15,368 | 263 | 64 | 391 | 0 |
| 954 | 15,365 | 252 | 65 | 382 | 0 |
| 955 | 15,369 | 263 | 72 | 407 | 0 |
| **Total** | | | | **2,389** | **0** |

Only **945 distinct complete masked component byte strings** occur across these 2,389 source-stage assignments; shared genuine source outputs recur under multiple geometry choices. The 945 distinct values all fail the unchanged original K04 commitment. Original cross-model candidate duplication is reported explicitly to prevent interpreting assignments as independent target evidence. A synthetic planted 16-byte component commitment was selected from the exact enumerated 945 and recovered **uniquely**, exercising the complete digest lookup.

A particularly useful structural finding is a **single stable, complete inferred unprinted 16-byte stream** across *all six* independent model vectors: `C9304FE833674EFD67B213839E4BA01D`, at output stage `p−254`, where `p` is the model's nominal selected stage 950..955. Its 32-bit high bits decode row93's **DEST rejected/rejected/bench** and the immediately following row94's **CLASS LABEL** in every model. This shared metadata bridge is an original-source-derived local generator prediction and a reproducibility check; it remains a **different printer interval** from the physical selected 18:02 coupon. The full six models still have the independently established conflicting metadata witnesses and no author-certified target-stage relation.

Executed local Python source-equivalent SFT `k04_six_stage_sft.py` with exact original resource bytes passed all six rank/count assertions, cross-model invariant, 945 distinct-candidate census and synthetic positive. Repo copy: [six-geometry SFT](../agents/agent44/k04_six_stage_sft.py). The remote source was committed/read back, and a Python integer-key correction was committed/read back; no remote CI run is claimed. The original evidence, acceptance, canonical candidate, and verifier remain unchanged.

The new bound is a **complete six-model alternative stage result for zero/one-free-bit fourword windows**. No unseen target coupon bit, no K08 final caption word, and no combined REC8 acceptance has been recovered.
