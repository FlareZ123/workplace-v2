# K04: original node50 all-row 4..11-draw chronology cut

**Agent 4 | 3 Nov 2026.** Original REC8/1 status: six individual PASS; K04 and K08 MISSING; combined INCOMPLETE. This study supplies a new **conditional source-producer falsifier**, not recovered selected coupon bytes.

## Mechanism and precise result

Under the previously reported printer **p951 MT19937 native-stage basis**, fit 132 original intact printer records, with selected disputed row129 completely withheld (original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; rank 15365). Convert each of the 64 original CRC-valid **node50 recorder CONTROL** values for sequence 7..70 into its native untempered 32-bit word (original raw recorder SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`).

Hypothesize a single printer-shared native MT stream with source-anchored node50 **seq7 at stage -810** and **4..11 generator words per consecutive original node50 sequence**. Before imposing any recorder-to-recorder equations, enumerate every stage whose source-fixed printer bits agree with the observed recorder value. Exact dynamic programming over all 64 consecutive records shows **first failure at seq34**, without needing to assume the position of seq70.

The full unsatisfiable-prefix witness is short:

* After placing every original seq7..33, only **two seq33 native stages, -630 and -629**, survive.
* The next 4..11-word gap forces seq34 into **-626..-618**.
* The nine candidate stages disagree with source-fixed original printer bits by **16,12,5,1,19,13,15,12,18** bits respectively. The closest case -623 has fixed native mask `80000001` and fixed value `00000001`, while original seq34 untempers to `3096C886` and has both masked bits zero. Hence even that one candidate contradicts one original source-fixed bit.

A separate exact maximum-weight subsequence DP, with both previously reported endpoint anchors seq7=-810 and seq70=-339, finds **at most 60/64 source-compatible CONTROL records**, with one maximum-size omission set **seq30,36,67,68**. This 60-row path itself fails a full joint-state test, so 60 is a **source-only ceiling**, not evidence that 60 jointly compatible historical observations exist.

## Boundary and new research implication

The previous 56-row [conditional target parity](h17-k04-first-conditional-target-parity-seq47-stage-ambiguity.md) omits eight real CRC-valid node50 controls. This new result establishes that its 4..11-draw **single-producer all-record extension cannot be rescued merely by choosing different native positions for every control while preserving seq7=-810**. At least one mode transition, record exception, out-of-band draw cadence, anchor change, or other producer architecture is necessary for an all-record explanation.

The falsifier is conditional on p951 shared-MT generation, seq7=-810, native CONTROL interpretation, and 4..11 draws per consecutive sequence. It cannot rule out intermittent separately sourced records or a genuinely different draw schedule. The actual K04 selected 128 bits remain unauthenticated; no K04/K08 acceptance test is claimed.

## Reproduction

[Single-file read-only source SFT](../agents/agent4/k04_node50_all_rows_source_cut_sft.py) imports the exact existing p951 basis, pins original printer and recorder SHA/CRCs, computes the DP witness, and checks a planted 64-row positive and tampered one-row negative. Locally executed original-source equivalent code produced the stated first failure, nine mismatch counts, 60/64 ceiling and controls PASS. The source, verifier, commitments and candidate were left untouched.

**Next experiment:** Fit a *historically interpretable* mixed-producer or adaptive draw-consumption model, predicting withheld original node50 controls/AUX fields before using any target-facing parity consequence. Extending the fixed 4..11 all-row model is mathematically blocked under these anchors.

## 16:24 UTC stronger cut: unbounded rejection gaps cannot rescue fixed seq33/36 anchors

The 56-row conditional history independently fixes original seq33 CONTROL at native **−630** and seq36 CONTROL at **−609**, omitting both original seq34 and seq35. This gives a stronger local question than any 4..11-per-record bound: *could seq34 be inserted anywhere in the strictly increasing native interval* **−629..−610**, if the writer consumed arbitrarily many hidden MT draws?

**No.** Every one of those 20 native stages has at least one original-printer-fixed bit conflicting with the untempered original CRC-valid seq34 CONTROL `3096C886`. The closest interior stage **−623** has source-fixed mask `80000001`, source-fixed value `00000001`, and one conflict against `3096C886`. This exclusion uses no seq34 stage assumption, event/AUX/latch hypothesis, or rejection limit. The [extended original-source SFT](../agents/agent4/k04_node50_all_rows_source_cut_sft.py) asserts all 20 failures and checks that a synthetic source-compatible seq34 replacement at −623 succeeds.

**Precise scope:** Under p951 and the frozen positions seq33=−630/seq36=−609, **no number of added rejected draws anywhere between them** can place the authentic seq34 CONTROL on the same monotone MT stream. A rescue must move at least one of those positions, adopt a different producer/state or interpretation, or drop the single advancing-stream premise. It is incorrect to treat one exceptionally long CPython `randrange` rejection chain by itself as sufficient. The selected K04 stage and final K08 wording still have no recovered authentic values.
