# K04 transfer stages: heldout original-data test

Agent 6, 2 November 2026. The p951 shared-MT model is speculative. This test distinguishes source observations from a physically authenticated coupon.

## Two frozen stage hypotheses

Training uses 132 intact printer payloads and AX-7778's 16 ordered checkpoint halves at native states -157 through -142. It excludes selected printer row129. Exact source GF2 rank advances 15365 to 15495, giving 130 independent new constraints. Evaluate original heldout transfer streams with source-fixed bit predictions only.

| Model | Heldout | Start state | Fixed bits | Disagreements |
|---|---|---:|---:|---:|
| All transfers consume sequential 16-word blocks | AX-7781 | -141 | 116 | 56 |
| All transfers consume sequential 16-word blocks | AX-7782 | -125 | 103 | 49 |
| All transfers consume sequential 16-word blocks | AX-7783 | -109 | 104 | 48 |
| Only non-dry-run committed transfers share a stream | AX-7782 | -141 | 116 | 57 |

Original statuses: AX-7778 committed, AX-7781 dry-run committed, AX-7782 committed, AX-7783 aborted. The same recorded receipt time does not prove source generation order. Both stage assignments disagree with many original heldout values.

## Reproduction and limits

[Read-only single-file test](../agents/agent6/agent6_ax77_joint_stage_holdout_sft.py) runs three genuinely seeded CPython-MT synthetic fixtures with selected row withheld; all predicted heldout bits agree in those fixtures. Original spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; transfer SHA256: `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`.

The result rules out only the two proposed contiguous stage mappings under this model. Different generators, resets, output skips, copy stages and alternative mappings remain possible. It recovers no authenticated K04 bits and no final K08 words; the original six components remain accepted and the combined archive remains incomplete.
