# K08: calibrated N07 reversal applied once to the fixed P20 payload is commitment-negative

**Agent 14 | 28 November 2026 | deterministic complete-output editor | no recovered K08 component**

## Why this is different from the aligned palette

The same-day aligned-source result exhaustively falsified a large family with per-position free choices. The 12:22 Critic correctly noted that such a palette is not itself an authoring rule.

This test instead freezes **one carrier and one operation** before acceptance:

- **carrier:** the 13-token N20 semantic payload already fixed by the independent AT/MT/ET/PT source chain and its PT stop boundary;
- **operation:** the N07 reversal instruction already calibrated target-blind by the source-emitted AES -> SEA transformation and the LOW/WOL count reversal.

No token choice, row choice, insertion, deletion, synonym, rotation, or ordering parameter remains after those two selections. The hypothesis is simply that the calibrated reversal operation is the final version transform on the fixed P20 payload.

## 28 November source-selector upgrade: the address chain itself selects N07

A later same-invocation composition removes most of the original operator-selection hypothesis.

The fixed payload decoder's ordered addresses are:

`AT -> MT -> ET -> PT`

Their second coordinate is invariant (`TTTT`), while the information-bearing first coordinate is `AMEP`. Apply the already-established ASCII LOW BIT packing, first bit as LSB:

- LOW BIT(`AMEP`) = **7**, selecting **N07**;
- LOW BIT(`TTTT`) = **0**, which is outside the N01..N24 note namespace.

The four address pairs are already fixed in payload order by independent source paths; no address permutation is introduced here. The changing address coordinate therefore supplies a direct source-local selector for the same N07 reversal instruction previously imported only by analogy from the AES/SEA calibration.

A dedicated reproducer rechecks all four address-pair overlaps against N20, the P20 payload fingerprint, AMEP->7, TTTT->0, the historical N02 reducer fixture and the single reversed-P20 acceptance outcome.

This **does not** prove that the selected N07 operation's operand is the completed P20 payload. That remains the one semantic composition edge. But the operator choice itself is no longer free.

Reproducer: `agents/agent14/k08_p20_address_heads_reversal_sft.py`

## Source-vs-free decision ledger

| Decision | Status |
| --- | --- |
| N20/P20 13-token carrier and stop | fixed by the independent AT/MT/ET/PT chain |
| Reversal operation | fixed and target-blind calibrated by AES -> SEA through N07 |
| N07 operator selection | **source-selected by AT/MT/ET/PT varying heads AMEP -> LOW BIT 7; invariant TTTT column -> 0** |
| K08 normalization/HMAC16/SHA256 reduction | fixed by the preserved route and acceptance |
| Apply the selected N07 reversal to the completed P20 payload | **remaining hypothesis; the operand edge is not explicitly attested** |
| Per-word choices / lexical substitutions / target-selected completion | none |
| Complete authored same-operation holdout | none survives; AES -> SEA is an operator micro-control, not an authored-caption holdout |

This is therefore a one-output falsifier of a specific missing edge, not evidence that Emily historically used reversal.

## Original outcome

The single complete normalized output was checked through the unchanged original K08 reduction.

- emitted complete candidates: **1**
- original K08 commitment hits: **0**
- P20 source fingerprint: PASS
- historical N02 reducer fixture: PASS
- calibrated reversal micro-control from the source network: AES -> SEA / LOW -> WOL

The identity P20 candidate and the two fixed WRAP-2 directions are also commitment-negative in the same-day aligned report, but they are not counted as part of this one-output reversal editor.

## Consequence

The source-calibrated N07 reversal does **not** close the missing P20 -> final-envelope edge. This is a more discriminating negative than expanding the aligned palette: it falsifies one exact whole-editor hypothesis with no fitted word decisions.

The unresolved requirement is now sharper. A successful K08 path still needs a surviving source relation that selects a different complete version operation or an independently preserved final carrier. Reversal should not be reintroduced through additional word palettes or arbitrary rotations unless a new record specifically selects that composition.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing; REC8/1 remains incomplete.

## Reproduction

The complete output is a strict member of `agents/agent14/k08_13word_aligned_source_editor_sft.cpp` under `reverse` with the P20 row selected at all 13 positions. A separate direct local reduction of that one output reproduced the same **MISS** against the unchanged original commitment.
