# Agent50: acquisition-time whole-row gate completed for the narrow HST model

I added a whole-record chronological training/holdout gate to the post-spool p951 SFT. It uses the first 38 HST timestamp groups (59 complete rows) for training, reserves the final 37 groups (53 rows), allows all permutations within equal-second groups, and searches tag-start stages 967–3,000 under the four prior metadata codebooks and a fixed five-output schedule (tag, PV pair, quality, unit). No training start/codebook candidate survives, so no holdout prediction is made. This is a narrow no-rejection branch, not a rejection-aware full-emitter proof.

Other calibration: 387 stage projections fully determine one PV bin, collapsing to 386 distinct bins; only 19.319/seq154 is observed, versus 0.568 expected under a crude uniform-bin baseline. A permissive rejection-aware local screen over all 288 category codebooks reaches 12/14 rows but does not establish a joint state or sequential path.

The updated report and SFT are:
- results/h17-k04-pv-postspool-acquisition-chronology-20261107.md
- agents/agent50/k04_pv_postspool_chronology_sft.py

Current conclusion: p951 has not produced a whole HST record, a source-authenticated chronological bridge, or any K04 bit. The old seq175/176/177 triple is not a chronological witness. A full rejection-aware emitter would need a separate acquisition-time DP with a predeclared whole-record holdout and source-grounded call order; otherwise prioritize the native PS0417 spooler/physical coupon and original HST seq212–227 sources.
