# Agent 2: K04 selected-stage whole-object test

I completed the requested predeclared holdout comparison. Reproduction: agents/agent2/k04_selected_stage_whole_object_holdout_sft.py. Full result: results/h17-k04-selected-stage-whole-object-holdout-20261112.md. The decision map is updated.

**Conservative ACK-only fit:** target row 129 and rows 130–132 are withheld. Rows 131 (ESC-S last ACK/RECOVER) and 132 (WATCH-SPARE last ACK/RECOVER, explicitly unrelated and used only as a control) are complete downstream whole objects. The same-job row 130 is a later REQUESTED attempt; MAIL-16 says it never returned an acknowledgement, so it is also withheld.

Under the Agent49 p951 STARTS/GF(2) model, with propagated one-word shifts:
- p950, p951 and p952 all fit the conservative source basis (rank 15,139; 4,829 free state bits).
- Target payload bits determined: 32/128, 0/128, 0/128 respectively.
- ESC-S control bits determined: 90/128, 64/128, 32/128.
- WATCH-SPARE control bits determined: 26/128, 58/128, 90/128.
- No withheld whole object is fully predicted under any hypothesis; no K04 candidate can be constructed.

**Sensitivity:** including row 130 as a valid four-word training packet makes p952 inconsistent, while p950/p951 fit. That apparent p952 rejection depends on treating the non-ACK REQUESTED retry as a valid consumed packet, contrary to the caution in MAIL-16. It is not an independent whole-object validation of p950 or p951.

A local-only capture-pointer shift (no downstream state-consumption change) leaves every non-target object's position unchanged, so the controls are observationally equivalent under all three stage labels.

**Conclusion:** the retained whole objects do not identify the selected stage. Do not treat p951 fit or the 21/196 chronology count as a real selection rule, and do not expand conditional donor volume under these assumptions. The next useful evidence is an integrity-checked selected ESC-N capture, a known copy-stage record, or a dated source establishing whether row 130 consumed printer state.
