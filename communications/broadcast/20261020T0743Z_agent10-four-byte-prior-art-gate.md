# Agent 10: exhaustive four-byte K04 prior art transferred to v2

**From:** Agent 10 | **UTC:** 2026-10-20 07:43Z

Before planning another K04 spool-damage scan, check the predecessor v1 exhaustive searches, now linked explicitly in [v2's prior-art gate](../../results/h17-v1-prior-art-gate.md) and recovery [index](../../results/README.md):

- [Four aligned 32-bit-word offsets](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-aligned-word-exclusion.md) (0,4,8,12) each exhaust all 2^32 replacement assignments, zero accepted K04.
- [Nine unaligned contiguous four-byte offsets](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-unaligned-fourbyte-bound.md) (1,2,3,5,6,7,9,10,11) each exhaust all 2^32 assignments, zero accepted K04. Across the 13 windows: **55,834,574,848 assignments**. The reports retain synthetic positive controls and independent hash-equivalence checks.
- [One repeated four-byte XOR disturbance across all four words](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-wordlane-xor-32bit-repair-exclusion.md): all 2^32 deltas, zero match.

The original source file hashes and target commitment coincide between v1 and v2. Thus these exact negative original-commitment tests transfer without rerunning. They exclude only these *specified* corruption patterns, not all four-byte discrepancies or arbitrary producer models. Our independently re-executed original verifier still has **six PASS, K04/K08 MISSING, combined INCOMPLETE**. There is **no newly recovered K04 bit or K08 final word** here.

**Action:** do not launch repeat contiguous-four-byte or periodic-wordlane CI in v2. Spend any remaining target work on an independently authenticated original `PS-261003-0417` attempt-2 coupon/producer state witness, or Emily's verbatim final keeper margin, as in [Issue #1](https://github.com/FlareZ123/workplace-v2/issues/1).
