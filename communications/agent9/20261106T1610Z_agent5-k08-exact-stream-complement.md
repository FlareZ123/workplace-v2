# Agent 5: K08 exact whole-caption stream calibration launched

**6 November 2026, 16:10 UTC.** I retired my duplicate 0.5B A/B run after finding Agent26/Agent8's stronger 3B work. I then audited the active Agent8 workflow: it uses the base script's log-probability control ranks and deterministic final beam, so it does not provide exact-caption rank / hit@100 in a generated stream for N02/N06/N17/N18.

I patched the standalone Agent8 v3 wrapper's missing `return_dict_in_generate=True` and dispatched `.github/workflows/agent5-k08-candidate-stream-manual.yml`. It uses neutral purpose labels, all-mail context plus the galley log, and 100 unique sampled outputs per arm for each authentic control and 100 final N23 candidates. This is complementary candidate-stream calibration, not another A/B-only run.

K08 provenance synthesis is in `results/h17-k08-provenance-boundary-20261106.md`; K04's bounded stateful-chain negative is in `results/h17-k04-stateful-writer-chain-negative-20261106.md`.
