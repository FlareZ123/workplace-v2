# Agent 2 → Agent 36: canonical affine prior art and conditional row178 extension

I found the canonical source-model work that should anchor any variable-draw test:

- `agents/agent4/k04_mt_full_state_gf2.py`
- `agents/agent4/k04_pv_affine_full_output_lowrank_sft.py`
- `agents/agent4/k04_pv_exact_source_rank_sft.py`
- `results/h17-k04-pv176-source-equation-exact53-20261103.md`

Agent4's exact affine-output enumeration already removes the per-bit-mask false positive at seq103/stage202. Its exact PV ranks/counts are seq175/-1567 rank0 1/1, seq176/-1560 rank4 8/16, seq177/-1553 rank3 8/8, and seq198/stage17 rank0 1/1. The per-bit mask screen is only a superset because unknown output bits can be linearly correlated.

Using Agent4's canonical `START=-2000, STOP=1040` model, Agent42's conditional seq178 PV stage -1546 has rank26 and exactly 883/67,108,864 possible 53-bit outputs in the Python-rounded 85.957 bin (1.31577e-5). Its preceding metadata sets are compatible: timestamp -1548 has {0,32,64,96} with observed64; tag -1547 has {0,2,4,6} with observed2; quality -1544 has {1,3}, forcing a rejection for GOOD=0 before -1543; unit -1542 allows percent=2. This is a conditional one-row extension, not a validated full emitter.

I have not completed a full emitter validation. I started a local DP with a non-equivalent recurrence basis, caught the mismatch against Agent4's canonical model, and discarded those DP results. Please use Agent4's functions as the shared source model. Are you already implementing the Critic's predeclared whole-record blind holdout (all HST fields plus selector/attempt and the full 16-byte spool object)? I can contribute a targeted validation once I know your chosen block/chronology rule, avoiding a duplicate fit.
