# K08: blind source-masked historical author/purpose ranker (6 November 2026)

> **Correction 6 November, ~12:00 UTC:** The original four-case run inadvertently retained the *competing N17 or N18 inscription* as an exact quotation within MAIL11 even when that candidate's own N-record was withheld. Consequently, the **N17 and N18 reported ranks are contaminated**: their competitor received an unfair source-copy advantage. N02 and N06 genuine draft controls do **not** have this duplicated quoted competitor and their original ranks remain valid. The label-control figures below are retained as raw-run history, not usable blind author-ranking evidence. A [corrected quote-clean wrapper](../agents/agent9/k08_blind_author_rank_quote_clean.py) removes every complete decoy quotation in the mail body *before* normal control-word redaction, asserts non-leakage, and is being tested independently. This correction supersedes the earlier blanket claim that all decoys were absent from source excerpts.

**Agent 9 | original archive, complete successful four-job manual Actions execution.** This report tests whether historical author/purpose context distinguishes **genuinely withheld** complete captions better than generic caption language probability. It does **not** recover K08 or report a final-envelope caption. Original six K01/K02/K03/K05/K06/K07 individually PASS, K04/K08 unresolved, combined REC8/1 INCOMPLETE.

## Novel, exact heldout task

The [reproducible Qwen2.5-0.5B scorer](../agents/agent9/k08_blind_author_rank_sft.py) evaluates **mean next-token log probability of a proposed complete caption** after a genuine historical context. Four separate positive-control tasks are the original full Emily N02 and N06 draft sentences and distinct N17/N18 older-envelope labels. No heldout text is in its model prompt. Across each task:

1. Delete the heldout note in full. Redact **every exact normalized word type of that note wherever it occurs** in the remaining source excerpts, mail11/mail20, purpose description and instruction. Source masking asserts no forbidden word remains.
2. Select **11 authentic original note-line decoys** by ascending absolute word-length difference from the hidden original (ID is the deterministic tie-breaker). Delete all 11 decoy lines from the model prompt as well. These source-authentic decoys are only candidate outputs, never observed training examples in the task prompt.
3. Score the actual hidden normalized sentence and the 11 complete decoy sentences under two prompts, source text identical except the original case's note-purpose description versus generic 'a historical H-17 crew note'. No target digest or normalized caption is used to tune the rule.
4. Rank 12 complete candidates by length-normalized log likelihood, not by whether a sample happens to exactly reproduce the original. Ground-truth withheld strings are revealed to the scorer only after candidate construction and source masking, not provided to the model.

Model identifier: `Qwen/Qwen2.5-0.5B-Instruct` downloaded by each Actions job with `transformers==4.57.1` and PyTorch CPU float32. The source crew SHA256 is `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. An independent original N02 nonce-HMAC first-16 fixture matches `BF889359B0303F2B2B2FD96AE841210B`. Original route nonce and actual K08 acceptance target are pinned. Code and unmodified source pass all four `--smoke` tests before model execution.

## Completed authentic ranks

| Genuine historical caption withheld | Proper-purpose rank /12 | Generic-context rank /12 | Proper-purpose rank change |
| --- | ---: | ---: | ---: |
| Emily N02 first crew-board draft | **2** | 3 | improved by 1 |
| Emily N06 second desk draft | **5** | 7 | improved by 2 |
| Emily N17 standby envelope label | **3** | 2 | worsened by 1 |
| Emily N18 commissioning label | **10** | 11 | improved by 1 |

**All four jobs SUCCESS**, original-source GitHub Actions workflow run [42212585098](https://github.com/FlareZ123/workplace-v2/actions/runs/42212585098) (6 November 2026, 11:45–11:50 UTC). Each job prints the full 12-candidate list and model score in its own log, preserving result provenance. The role descriptions introduce semantic content but no literal heldout word survives the masking assertion.

## What this shows and does not show

The new source-masked ranking objective can place an entire real withheld Emily draft at rank2 among length-matched authentic alternatives, a distinct observation from Agent7's previous 0/15 exact Qwen2.5-3B cloze recall. The same 0.5B ranker is inconsistent across historical purposes (N18 at 10/12) and fails a deliberately strong source-author candidate selection threshold requiring both true N02 and N06 rank <=3. N17 purpose ablation harms ranking.

The baseline lacks a true final-version ancestor and has only four available historical Emily positives. The purpose effect is not independently estimated over many shuffled purposes. Mean token likelihood can favor ordinary syntax and residual source-vocabulary differences. Deterministic decoy selection by historical length and complete removal from model context restricts leakage; it does not prove the hidden N23 final words follow the same genre or that this scorer is calibrated to her terminal version. The original K08 full commitment is deliberately **not queried for a speculative final candidate under this weak 0.5B ranker**. No final caption is recovered or authenticated. A prospectively stronger ranker should first improve the two distinct genuine draft controls without target feedback; only then freeze complete final phrases and test original K08.

Repo changes include [source-pinned ranker](../agents/agent9/k08_blind_author_rank_sft.py), [manual workflow](../.github/workflows/agent9-k08-blind-rank-manual.yml), and a [targeted calibration critique request](../communications/agent49/20261106T1147Z_agent9-blind-author-ranking-critique-request.md). This is a new **source-selectivity experiment** rather than another grammar-cardinality result.

## Distinct original-source wrong-purpose counterfactual (6 November ~12:01 UTC)

The [four-job manual wrong-role run 42213764079](https://github.com/FlareZ123/workplace-v2/actions/runs/42213764079) retained the same historical hidden sentences, same 11 decoys, same word-type source redaction and model, but **swapped** the two draft-role descriptions (N02↔N06) and the two older-envelope roles (N17↔N18) *without reading K08 acceptance*. This is an actual executed intervention on purpose content, unlike a post-hoc comparison of invented final phrases.

For the **uncontaminated author-draft controls**, the original historical whole-sentence ranks were:

| Hidden authentic draft | Correct historical purpose | Wrong purpose swapped | Generic purpose | Correct-purpose mean token log probability | Wrong-purpose log probability |
| --- | ---: | ---: | ---: | ---: | ---: |
| N02 | **2/12** | 3/12 | 3/12 | -5.153006 | -5.189011 |
| N06 | **5/12** | 7/12 | 7/12 | -6.143317 | -6.410149 |

Both legitimate roles gave a modest improvement in actual source-blinded historical draft rank and true-sentence log likelihood. The older-envelope swap jobs are affected by the exact competing-label mail quotation identified in the correction above and are **excluded from this inference** until the corrected run completes. Two authentic positives are too few to establish predictive reliability, and neither one was the final keeper-envelope caption. The stronger 3B genuine-draft scorer is a separate ongoing preselected model-family check, not an escalation of raw K08 phrase-guessing.
