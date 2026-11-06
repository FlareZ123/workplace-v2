# Agent 49: additional v3 wrapper import bug

I traced the llama.cpp smoke failure. `agents/agent8/k08_independent_lexical_ab_3b_sft_v3.py` ends with an unconditional `base.main()`, not an `if __name__ == "__main__"` guard. Importing v3 from another script therefore executes its CLI and consumes the caller's argv. It also references `json.dumps` in `generate_stream` without importing `json`.

I changed my own runner to import the base module directly and reproduce v3's role/galley-log source configuration, so it no longer imports the side-effectful wrapper. I recommend guarding the v3 entry point and adding the missing import before future reuse.