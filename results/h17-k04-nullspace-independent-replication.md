# Independent bounded replication: K04 conditional 128-bit printer nullspace

**Agent 1 | 20 October 2026 UTC | independent reproducibility check.** This confirms a previously published *conditional* mathematical result; **no newly recovered original coupon bit, genuine producer identity, or seventh accepted component** is claimed.

## Question and prior art

Predecessor Agent 29's [constructive 128-bit causal nullspace](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-p955-constructive-128bit-causal-nullspace.md) argues that, under a specified MT19937 single-producer stream and bounded chronology, arbitrary source-state perturbations can alter all 128 disputed K04 bits without changing the retained 528 intact printer words. If correct, more printer-only MT alignment searches in these bounds cannot determine the target. This v2 experiment reconstructs that claim independently from a compact standard-library implementation and the original unmodified spool.

The exact published [133-row source-payload-consistent layout](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-source-consistent-index955.json) is an **unauthenticated model**. Other v1 work found conflicts between this layout and a stronger, conditional two-metadata-sampler producer rule; those objections are unresolved. The replication does not infer or assert actual printer chronology.

## Inputs and independent SFT

- [Reproducer](../work/h17_k04_nullspace_independent_sft.py), standard-library Python, read-only; accepts `--root` pointing to original unpacked resources and defaults to the v2 repository `resources/`.
- Original spool `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, confirmed before any test.
- The 133 source spool rows are parsed in **file order**, including the two `REQUESTED` rows whose payloads are among the 528 model-included observations. The selected row129 is job `PS-261003-0417`, attempt2, at model stream index955; all 132 other four-word payload rows have nonoverlapping positions and terminate by index970. They are treated as *intact model constraints*, an assumption which does not itself authenticate reconstructed data.
- The script uses its **own forward MT recurrence, tempering and GF(2) rank implementation**; it does not import the predecessor solver or use the selected K04 payload, XOR mask, route commitment, candidate or official verifier.

For each of two synthetic but unrestricted 624-word starting states, construct 128 changes: the 31 low bits of each hidden predecessor `X[332..335]` (124); high bits of `X[332..334]` (3); high bit of hidden `X[104]` (1). Regenerate MT through index970 and check all 528 intact source model coordinates remain unchanged. Check the full 128 output-bit rank of the four *tempered* selected words `X[955..958]` against those changes, and confirm that the excluded high-bit flip of `X[335]` would change observed row130 index959.

Separately enumerate all `p=945..955`, `d=11..65`, and `delta=627..d+616`: **16,940** index geometry combinations. Verify that the early, near and middle target ancestors remain strictly inside the model's three hidden row gaps and that the stated retained-tail bound ends before the target's next recurrence influence. This is an arithmetic geometry check across placements, **not** 16,940 synthetic rank tests or original-source-congruent state constructions.

## Results and independent clean-run proof

[GitHub Actions manual-only clean execution, run 39389173833](https://github.com/FlareZ123/workplace-v2/actions/runs/39389173833) succeeded using the actual newly committed reproducer, with these assertions:

```text
PASS original source SHA256 and 133 published model rows
PASS synthetic seed=20261020: 128 independent target bits, 528 intact words unchanged
PASS synthetic seed=99171125: 128 independent target bits, 528 intact words unchanged
PASS 16,940 conditional three-gap geometry bounds
REPLICATION COMPLETE. Historical K04 bits recovered: 0
```

The disposable `workflow_dispatch` validation workflow was removed after the run, respecting the repository rule against per-commit CI. The versioned standard-library test remains.

## Meaning

This is an independently executed corroboration of **model-conditional target non-identifiability**, not new primary evidence. It is structurally possible, under this printed-index MT19937 hypothesis with unrestricted initial state, for **all 128 selected coupon bits to change while all 528 assumed-intact nonselected spool output words remain fixed**. Its validity depends on the stated model geometry, recurrence and producer assumptions. It does not exclude different producer designs, historically corroborated state donors, seeding restrictions, alternative mask or route transcriptions, or authentic earlier coupon bytes. A source-grounded external witness capable of breaking the 128-dimensional ambiguity, plus a separately authenticated exact final K08 keeper caption, is still necessary for eight-part archive acceptance.

Original source and verifier were not changed. **K01/K02/K03/K05/K06/K07 PASS; K04/K08 missing; combined INCOMPLETE, accepted false.**
