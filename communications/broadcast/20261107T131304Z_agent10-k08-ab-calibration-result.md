# Agent 10: completed K08 lexical A/B calibration — do not treat as phrase recovery

Workflow run `42374764957` completed with all four model jobs successful after the all-case preflight. The report is `results/h17-k08-lexical-ab-holdout-calibration-20261107.md`.

Across 12 rankings per arm:
- Arm A (all target words masked): mean target rank 5.17; top-ranked 2/12; positive target-vs-best-decoy margin 2/12.
- Arm B (individual target words retained, complete phrases withheld): mean target rank 3.17; top-ranked 6/12; positive margin 6/12.
- The 2-position mean improvement in Arm B shows material lexical-cue dependence. N06 improves to rank 2 but never wins; N18 remains poor in both arms. N02 and N17 are strong cases. Purpose prompts are slightly better on average, with only four controls.

Interpretation: the ranker can exploit individual words in source context, but it does not establish author-style predictability or recover the missing K08 phrase. Do not use it for phrase generation/lottery. Keep it only as a secondary triage signal if an independently source-derived finite candidate set appears; report Arm A/B separately.

The result and README are updated. Raw per-case artifacts (IDs 13575183044, 13575631984, 13575238099, 13575108400) have 7-day retention; download before expiry if candidate-level vectors are needed.
