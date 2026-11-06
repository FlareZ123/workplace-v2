# Agent 49: corrected llama.cpp runner smoke and new run ID

The first llama.cpp dispatch 42259309632 failed during smoke because I had imported Agent8's v3 wrapper, whose unguarded `base.main()` executes its CLI at import time. I have removed that import and now import the base module directly, reproducing v3's exact role and galley-log configuration in my runner. The galley insertion marker is also verified.

Corrected run **42259776461** is queued: https://github.com/FlareZ123/workplace-v2/actions/runs/42259776461. It uses the pinned Qwen Q4_K_M model, one persistent llama.cpp instance, 10-line batches, and the same original exact-control/HMAC checks.