# K08 author-ranking calibration: paired lexical A/B holdout run 42374764957

**Status:** completed, four of four model jobs successful; all-case preflight passed. This is a calibration of the caption-ranking method, not a recovery of the K08 phrase.

## Question and design

Does the small historical-author ranker select a known held-out Emily caption from 12 candidates, and how much does retaining individual target words in source context affect ranking?

- Model: `Qwen/Qwen2.5-0.5B-Instruct`; `transformers==4.57.1`; CPU PyTorch installed by the workflow (exact torch patch version was not preserved in the artifact).
- Four held-out notes: N02, N06, N17 and N18. Each candidate set contains the true held-out caption plus 11 decoys.
- Three prompt conditions per case: purpose, generic and swapped-role.
- Arm A: remove the complete target/decoy phrases and mask every remaining occurrence of target words from the source prompt.
- Arm B: remove complete target/decoy phrases but retain individual target words in source context.
- The target phrase and decoy phrases are excluded from all model prompts; the target is included only as a scoring candidate. The preflight checks all four holdouts, all six prompts per holdout, candidate-key equality, strict Arm A word masking, and negative controls for missing/unexpected keys and target/decoy leakage.

Higher log-probability is better. `target_minus_best_decoy` is target score minus the best-scoring decoy; positive means the target beats every decoy.

## Case-level results

Ranks are ordered **purpose / generic / swapped**. Mean margins are averaged over the three conditions.

| Held-out note and target | Arm A ranks | Arm A mean margin | Arm B ranks | Arm B mean margin |
|---|---:|---:|---:|---:|
| N02 — “A good watch leaves the room ready for the next pair of hands.” | 2 / 3 / 3 | -0.199 | 1 / 1 / 1 | +0.260 |
| N06 — “The little lamp stays on until the corridor has gone quiet.” | 5 / 7 / 7 | -1.426 | 2 / 2 / 2 | -0.321 |
| N17 — “Leave the light on for the next watch.” | 2 / 1 / 1 | +0.161 | 1 / 1 / 1 | +0.841 |
| N18 — “Back before the first boat.” | 10 / 11 / 10 | -2.522 | 7 / 9 / 10 | -2.322 |

Across 12 rankings per arm:
- Arm A mean target rank **5.17**, target top-ranked **2/12**, positive target-vs-best-decoy margin **2/12**, mean margin **-0.997**.
- Arm B mean target rank **3.17**, target top-ranked **6/12**, positive margin **6/12**, mean margin **-0.385**.
- Retaining individual target words improved mean rank by **2.0 positions** and mean margin by **0.611**. The target-word masking control therefore materially changes ranking; apparent predictive power is partly lexical-cue dependent.
- Purpose prompts had the best mean rank in both arms (A 4.75; B 2.75), but the four-case sample is too small to establish a robust role-prompt effect.

## Interpretation

The ranker has some ability to identify familiar watch/room/light captions when lexical cues remain. It is substantially weaker when all target words are masked. N06 improves to rank 2 in Arm B but never wins; N18 remains poor in both arms. N02 and N17 are strong cases, while the result is not consistent across heldouts.

This is **not evidence that the ranker can recover the missing K08 phrase**. The model is a small pretrained ranker, the sample is four known captions, and the prompt/candidate set is constructed from the same small archive. The target phrase is deliberately withheld from prompts, but Arm B retains its individual words. The output is a diagnostic of lexical leakage and ranking calibration, not an author-style proof or a source of candidate wording.

## Decision

Do not use this result to generate or brute-force K08, and do not treat the Arm B advantage as authorship evidence. If a future original source supplies a finite, independently grounded candidate set, the ranker may be used as a secondary triage signal with Arm A and Arm B reported separately. The exact K08 phrase must still come from the original envelope, desk notes or photo/caption source and pass the acceptance HMAC.

## Reproduction and raw artifacts

- Workflow: `.github/workflows/agent36-k08-lexical-ab.yml`
- Run: `42374764957`; all-case preflight and all four matrix jobs succeeded.
- Preflight SFT: `agents/agent10/test_agent36_k08_lexical_ab_preflight.py`
- Runner: `agents/agent36/k08_blind_author_rank_lexical_ab.py`
- Raw per-case artifacts (7-day GitHub Actions retention):
  - N02: artifact `13575183044`, `agent36-k08-lexical-ab-case-2`
  - N06: artifact `13575631984`, `agent36-k08-lexical-ab-case-6`
  - N18: artifact `13575238099`, `agent36-k08-lexical-ab-case-18`
  - N17: artifact `13575108400`, `agent36-k08-lexical-ab-case-17`

The artifacts contain `ab-ranks.json` and `holdout-manifests.json` for each case. The runner and preflight are committed in the repository, so the run can be reproduced; the original artifacts should be downloaded before retention expires if full candidate-level score vectors are needed.

