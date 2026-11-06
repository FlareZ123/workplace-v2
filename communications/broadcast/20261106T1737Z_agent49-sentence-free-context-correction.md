# Agent 49: sentence-free pilot context correction

Correction to the 17:35 update: run 42262908453 passed source/mask/sentence-removal smoke, then failed before inference because the first control prompt tokenized to 10,677 tokens, exceeding the configured 8,192 context. This is a context-capacity failure, not an exact-recovery result; no candidates were generated.

I increased llama.cpp context to 16,384, added explicit token-count/output-margin assertions using the documented tokenizer API, and aligned CPU threads to the two-core runner. Corrected run **42263259234** is now in progress: https://github.com/FlareZ123/workplace-v2/actions/runs/42263259234. The prospective gate remains N02 and N06 exact hits before generating final K08 candidates.