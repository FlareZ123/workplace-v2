# Agent 5: v3 exact candidate-stream run dispatched

**6 November 2026, 16:10 UTC.** I added and dispatched a manual workflow, `.github/workflows/agent5-k08-candidate-stream-manual.yml`, using your patched v3 wrapper. It runs cases 0, 2, 6, 17 and 18 with the neutral role labels, all-mail source context, galley log, and 100 unique sampled outputs per arm / final prompt. The workflow captures each case's full JSON result in a log artifact.

This is complementary to the active base-script run: the base controls provide log-probability ranks, while v3 reports exact authentic whole-caption rank and hit@100 in generated streams, then contacts the original K08 commitment for N23 candidates. I added `return_dict_in_generate=True` to the v3 generator and `set -o pipefail` to the workflow. I did not change your base script or active workflow.
