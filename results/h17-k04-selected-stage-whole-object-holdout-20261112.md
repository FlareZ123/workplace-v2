# K04: selected-stage hypotheses tested against predeclared whole-object controls

**Agent 2 | 12 November 2026 | Source-pinned holdout experiment.** K04 remains unrecovered. This test directly addresses the current p950/p951/p952 ambiguity; it does not treat a compatible chronology count as evidence of a real capture rule.

## Predeclared hypotheses and controls

The base is Agent 49's p951 symbolic MT19937 source model and its 133-entry STARTS schedule. The selected ESC-N job is PS-261003-0417; the last acknowledged RECOVER attempt is row 129 (attempt 2), whose 16-byte payload is the target under investigation.

Three one-word capture-stage hypotheses were declared:

- **p950:** the selected four-word capture block starts one output word before the p951 baseline.
- **p951:** it starts at the baseline output word 951.
- **p952:** it starts one output word after the baseline.

For the propagated-shift interpretation, every downstream row moves by the same delta (-1, 0, +1). The following controls were selected from route/selector metadata before fitting; their bytes are withheld in the strict model:

1. **Same-job earlier request, row 128:** PS-261003-0417 attempt 1, RECOVER/REQUESTED.
2. **Same-job later request, row 130:** PS-261003-0417 attempt 3, RECOVER/REQUESTED. MAIL-16 explicitly says this later button press never returned an acknowledgement.
3. **ESC-S control, row 131:** PS-261003-0448, last ACK RECOVER object for that route.
4. **WATCH-SPARE control, row 132:** PS-261003-0420, last ACK RECOVER object for that route. MAIL-16 calls it unrelated to K04; it is used only as a same-length printer control, never as a K04 donor.

## Results

### Strict non-ACK-withheld fit

The target and all four controls (rows 128–132) are withheld. Both same-job REQUESTED attempts are excluded rather than assuming that an unacknowledged request consumed a valid four-word packet. For each stage hypothesis, all remaining source equations are fit with the same GF(2) MT basis.

| Hypothesis | Basis rank | Free state bits | Target bits determined | Earlier REQUESTED row 128 | Later REQUESTED row 130 | ESC-S row 131 | WATCH-SPARE row 132 | Whole-object matches |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| p950 | 15,074 | 4,894 | 0 / 128 | 58 / 128 | 0 / 128 | 90 / 128 | 26 / 128 | None |
| p951 | 15,074 | 4,894 | 0 / 128 | 58 / 128 | 26 / 128 | 64 / 128 | 58 / 128 | None |
| p952 | 15,074 | 4,894 | 0 / 128 | 32 / 128 | 58 / 128 | 32 / 128 | 90 / 128 | None |

All three propagated-shift hypotheses fit the strict source basis. No withheld whole object is fully determined under any hypothesis. No K04 payload or component can be constructed from these partial predictions.

### REQUESTED-row sensitivity

The script separately tests three diagnostic fits:

| Fit variant | p950 | p951 | p952 | Consequence |
|---|---|---|---|---|
| Include earlier REQUESTED attempt 1 only | fits, target 32/128 bits | fits, 0/128 | fits, 0/128 | Partial p950 support depends on using row 128 as training; no whole object predicted |
| Include later REQUESTED attempt 3 only | fits | fits | inconsistent | p952 rejection depends on using row 130 as training |
| Include both REQUESTED attempts | fits | fits | inconsistent | Same p952 sensitivity; no whole object predicted |

The p952 contradiction is therefore conditional on treating row 130—a REQUESTED button press that MAIL-16 says never returned an ACK—as a valid consumed packet. It is not an independent whole-object validation of p950 or p951. The partial p950 target bits likewise appear only when the earlier REQUESTED row is used as training. Neither diagnostic supplies a complete selected object.

## Interpretation

- **No predeclared whole-object discriminator was found in the retained downstream controls.** The two complete ACK/RECOVER control payloads are not fully predictable from the other retained objects under any of the three propagated-shift hypotheses.
- **p950/p951/p952 remain unidentifiable under the strict evidence model.** The apparent p952 rejection depends on the later REQUESTED row; the partial p950 target bits depend on the earlier REQUESTED row.
- **A local-only capture-pointer shift is observationally equivalent on all non-target rows.** If the capture point moves but the printer's downstream state consumption does not, the non-target controls retain the same positions under p950/p951/p952 and cannot distinguish them. Only the missing target bytes or an independent media-integrity observation could resolve that case.
- The result is conditional on Agent 49's p951 STARTS schedule and linear MT model; it does not independently prove that schedule. It does, however, falsify the claim that the currently retained whole-object controls validate a unique selected stage.

**Research decision:** stop treating the 21/196 source-compatible chronology count or the p951 fit as evidence of a real selection rule. Do not spend more compute widening conditional donor volume under these same assumptions. The next useful evidence would be an independently integrity-checked capture of the selected ESC-N bytes, a known copy-stage record, or a dated source that establishes how the REQUESTED attempts consumed (or did not consume) printer output state.

## Reproduction

The standard-library test is agents/agent2/k04_selected_stage_whole_object_holdout_sft.py. From the repository root:

    python agents/agent2/k04_selected_stage_whole_object_holdout_sft.py --root resources

It pins the spool, route map, MAIL-16, routing record and acceptance file; resolves last-ACK selectors from the current route table; withholds the target and predeclared controls; and reports strict and diagnostic fits. No official source, route, acceptance commitment, verifier, or canonical candidate was modified.
