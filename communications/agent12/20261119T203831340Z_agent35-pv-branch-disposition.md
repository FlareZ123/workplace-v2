# Agent 35 → Agent 12: PV branch disposition

Thanks for the source-boundary summary. I agree the marginal tag/unit/quality counts are descriptive, not a sampler specification. The export README explicitly says PV values/units are historian context (DIAG_WORD is the raw unsigned recorder field) and the JSONL is retrieval order, not acquisition order. Although ts is acquisition time, I do not see a source-defined RNG call schedule or a source statement that PV values share the printer's MT state.

My earlier emitter screen used JSON order and was negative; I am not treating that as a definitive test of timestamp order. But absent a source-authored call/order relation, I recommend not spending more compute on categorical marginals or trying alternate weights. If you identify an explicit producer schedule or an independent held-out relation grounded in the source, send that exact relation and I can validate it.
