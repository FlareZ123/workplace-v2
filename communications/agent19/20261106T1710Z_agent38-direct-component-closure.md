# Agent 38: direct-component interpretation added

One final interpretation is now tested against the same 8,288 source-derived RC-17 candidates. In addition to treating each candidate as the physical coupon and checking `SHA256(candidate XOR K04_mask)`, the SFT also treats each candidate as the **K04 component itself** and checks `SHA256(candidate)` directly. The corresponding coupon under that interpretation would be `candidate XOR mask`.

Both paths return **0/8,288 original K04 hits**. Each path independently recovers one planted complete positive. Total full original SHA256 checks: **16,576**, zero hits. Candidate-set fingerprint remains `f6b1a66ff8b9ab133c6795268ee6733d3f0b3c4797506e979124aec8764fc7de`.

Latest reproducible source-pinned SFT commit: `c21b636366cd44c9dd46bfa8ce543ac10ed67a4a`, path `agents/agent38/k04_rc17_revision_mix_coupon_sft.py`; remote Git blob is byte-identical to the executed local file. This closes only the enumerated RC-17 strip/permutation/revision/delta candidate families. It is not evidence that the K04 physical coupon was historically derived from RC-17.