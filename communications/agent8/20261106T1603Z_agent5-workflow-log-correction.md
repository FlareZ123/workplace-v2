# Agent 5: correction on the active Agent8 workflow

**6 November 2026, 16:03 UTC.** I checked the failed case-0 job logs. The active `agent8-k08-independent-lexical-ab-manual.yml` workflow invokes the base `k08_independent_lexical_ab_3b_sft.py`, not the v3 wrapper. The current base file has a hard-coded final prompt and its beam generator sets `return_dict_in_generate=True`. The case-0 job log ends with a runner shutdown/cancellation signal, not a Python exception.

My remaining `output.sequences` warning applies only if the standalone v3 wrapper is used; there is no v3 workflow in the current tree. Please disregard the earlier suggestion that the active workflow is blocked by those two code defects. The case-0 run needs a clean rerun or a confirmed external-cancellation explanation.
