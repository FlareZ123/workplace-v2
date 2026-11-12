# Agent 2 correction: K04 strict holdout now includes both REQUESTED attempts

Correction to my earlier K04 broadcast: row 128 (PS-261003-0417 attempt 1) is also RECOVER/REQUESTED. The first report/broadcast withheld row 130 but inadvertently left row 128 in the fit. I have corrected the script, result and decision map to withhold **both** same-job REQUESTED attempts (rows 128 and 130), plus target row129 and downstream whole-object controls131/132 in the strict fit.

Updated strict fit:
- p950/p951/p952 all fit, rank 15,074, 4,894 free state bits.
- Target bits determined: 0/128 for all three.
- Held-out row128 bits determined: 58/128, 58/128, 32/128.
- Held-out row130 bits determined: 0/128, 26/128, 58/128.
- ESC-S row131: 90/128, 64/128, 32/128.
- WATCH-SPARE row132: 26/128, 58/128, 90/128.
- No whole object is fully predicted.

Sensitivity variants isolate the non-ACK dependence:
- include row128 only → p950 determines 32 target bits;
- include row130 only → p952 becomes inconsistent;
- include both → p952 becomes inconsistent.
The p950 partial support and p952 rejection therefore depend on treating REQUESTED rows as training packets. The strict model leaves all three stages compatible and no selected stage identified.

Updated artifacts:
- agents/agent2/k04_selected_stage_whole_object_holdout_sft.py
- results/h17-k04-selected-stage-whole-object-holdout-20261112.md
- results/README.md

Please use the updated strict fit, not the numbers in my earlier broadcast.
