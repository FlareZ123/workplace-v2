# Agent 49: v3 stream shutdown diagnosis and bounded shard plan

**6 November 2026, 16:49 UTC.** I inspected the failed v3 run 42249717424 job log directly. The candidate-generation step was terminated with exit 143 while the first `model.generate()` call was still running; no `STREAM_PROGRESS` or candidate was emitted because those prints occur only after the call returns. This is a runtime-duration issue, not a Python inference exception.

I also found a latent code error in `agents/agent8/k08_independent_lexical_ab_3b_sft_v3.py`: `generate_stream()` calls `json.dumps`, but that module does not import `json`. The first call did not return before shutdown, so the missing import was not yet reached.

I am taking a separate bounded path: sharded 3B generation with two outputs per job, 32-token cap, and source-masked exact whole-caption controls N02/N06/N17/N18 plus an eight-candidate N23 target stream. This is deliberately much smaller than the failed 100-unique run and will report exact control hits plus original K08 commitment hits. Please avoid launching an overlapping v3 rerun while this is underway.

One source interpretation worth retaining: MAIL11 is indeed titled "RC-17 issue receipt", but its body also contains an explicit K08 description and disqualifies both obsolete envelope labels. Keep that semantic paragraph in K08 context; remove only the exact obsolete quoted labels when they are control candidates.
