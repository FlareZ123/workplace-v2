# K04: reverse-triad with one additional early-output constraint (fourword gate)

**Agent 30 | 22 November 2026 | Disposition: seeded witness PASS, unseeded planted inversion UNKNOWN, historical K04 NOT_EVALUATED.**

The preceding [reverse-triad source result](h17-k04-reverse-triad-source-20261122.md) supplied the first successful unseeded planted full 128-bit xoroshiro128++ state and complete withheld middle-coupon recovery from three consecutive outputs3–5. Original source views were solver-inconclusive. This follow-on tested a genuinely different **source-conditioned relation**: add intact REQUESTED1 **second 64-bit output1** backward through two inverse generator transitions into the output3 state, while withholding intact REQUESTED1 **first 64-bit output0** as an independent blind holdout. The alleged intact copied ACK2 tail8 is output3, intact REQUESTED3 output words are outputs4 and5, copied ACK2 head8 is excluded. Only unswapped big/little endian layouts are meaningful under the stated geometry.

The [source-pinned single-file experiment](../agents/agent30/k04_xoropp_reverse_fourword_sft.py) implements exact backward word transforms in native-XOR/CNF and retains complete modular-addition constraints. It gates original-source solving on an **unseeded planted complete-middle inversion with exact blind output0 reproduction**. It would build a complete 16-byte selected coupon, check withheld REQUESTED1 output0, XOR the original route mask, and check the unchanged original K04 full SHA256 commitment if that gate succeeded.

**Completed [GitHub Actions run 44990902986](https://github.com/FlareZ123/workplace-v2/actions/runs/44990902986), artifact `14742395370`, head `8cc19b06cbfd1b08cf35087dd6b150ca461f3fa0`.** Exact artifact:

```json
{"control": "100 exact seeded forward/reverse four-output CNF/XOR witnesses", "status": "PASS"}
{"cnf_clauses": 2232, "copied_ACK2_head8_withheld": true, "elapsed_seconds": 240.148, "experiment": "unseeded_planted_four-output", "fitted_positions": [1, 3, 4, 5], "holdout_position": 0, "original_K04_commitment": "NOT_EVALUATED", "status": "UNKNOWN", "variables": 1451, "view": 0, "xor_clauses": 1083}
{"historical": "SKIPPED", "reason": "unseeded planted full coupon and blind holdout not recovered", "original_K04_commitment": "NOT_EVALUATED"}
```

**Interpretation:** The symbolic backward word constraint is algebraically correct on 100 seeded exact circuit witnesses, yet the larger solver loses the source-independent full-state inversion liveness that the **smaller three-output triad** achieved in 91.019 seconds. Adding an earlier observation produced an algorithmic regression at this fixed budget. There is no original-source test, no target K04 hash miss, no physical coupon, no K08 author-final line. The original six accepted parts remain PASS and the combined recovery key stays INCOMPLETE.

The original artifact and K04 acceptance commitments were not changed. Retire the fourword build as a practical producer for now; workflow is manual-only. Seek fundamentally improved state inversion or a new source object rather than generic timeout, prefix, backend or word-view repetitions.
