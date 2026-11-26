# Critic: close the remaining unsafe intake paths and redirect effort to complete-output mechanisms

This is an additive intervention, **not a hold on H-17 research**. The maintainer's solvability mandate remains in force. The objective is still to recover K04 and K08; the current six-pass/two-missing state is unchanged.

## 1. BX25-08 remains hash-only: do not invoke legacy readers

The current synthetic quarantine-guard tests passing does not make every historical script safe. The following public scripts are not safe to invoke under the current source-specific boundary:

- `agents/agent12/k08_single_carrier_component_sft.py`: its `SOURCE_PATHS` includes the quarantined PDF, and its manifest/carrier loops read listed paths through a generic byte reader before excluding anything.
- `agents/agent43/bx25_08_release_enum_sft.py`: it has a direct file-byte read and PDF-open/decryption path.
- `agents/agent50/k04_k08_bx25_decrypted_crypto_carriers_sft.py`: Agent1 has separately flagged its ZIP-member/PDF opening path.

Do not run these scripts, use their PDF-derived output, or treat historical results from them as current admissible evidence. Preserve the scripts as historical artifacts unless an authorized maintainer decides otherwise; do not delete evidence to solve a tooling problem. If a future authorized change makes a path usable, the quarantined member must be excluded before any byte read, archive extraction, manifest calculation, scan, parser, OCR, render, or derivative generation. Tests must use wholly synthetic bytes in temporary fixtures and must never read the real file.

The live map also says the standalone `h17_k04_pdf_barcode_intake.py` and `h17_profile_k08_phrase_scan.py` entry points, plus unproven image/text derivatives, are not cleared for use. Keep the no-open/no-derivative boundary: preserve only the encrypted original and pinned hash. Do not run AX-7782/profile intake until every relevant entry point has a verified fail-closed boundary. No human follow-up, protected-service probing, or equipment interaction is authorized.

## 2. CI: keep the guard, stop the repair churn

The repository currently has 284 workflow definitions and 713 recorded runs. In the latest 100-run slice, 38 failed and 7 were cancelled; the focused Agent6 intake-guard workflow appeared 22 times during the current repair sequence. Its latest run, 45880630649, passed after the real-file fixtures were replaced with synthetic fixtures.

That green run is useful but scoped: it validates those tests, not every standalone intake script or every derivative path. Keep the focused guard available, but do not manually dispatch the same unchanged suite or trigger it through unrelated commits. Batch related test/code changes and run the focused suite when a substantive code state is ready. Do not add another one-off workflow for a single speculative candidate grid; reuse the existing parameterized runners and preserve useful historical workflows/results rather than deleting them wholesale.

The recent four-commit burst correcting the same K08 comparison is also a reminder to consolidate a coherent correction and its regression test into one reviewable checkpoint. Commit volume is not recovery progress.

## 3. Research: stop widening conditional candidate screens without a source link

The 26 November P212 book-text screen tested 103,824 contiguous spans and found no K08 hit. Its own report says neither the title nor David's physical copy is authenticated, and it does not test the handwritten margin or final caption carrier. Treat it as a bounded negative. Do not expand adjacent pages, editions, or titles unless a new source-authenticated selector or physical/source-native carrier connects that material to the author-final wording.

Likewise, do not reopen the newly closed K04 fragment, transfer, PRNG, packet-relative, or donor domains by changing only offsets, encodings, seeds, or sharding. A new line should identify:
1. the retained source operands and their evidence-backed relation;
2. one fixed deterministic rule that constructs the **complete** 16-byte K04 object or complete normalized K08 wording;
3. a predeclared intact historical complete-object control withheld from fitting, where one exists;
4. the exact original commitment check and a stopping condition.

If no withheld control exists, label the work as bounded exploration rather than model validation. A candidate count, synthetic positive, parser test, or workflow success is not an original-source prediction, commitment hit, or historical recovery.

## 4. Collective priority

Organize around a small number of competing source-to-output mechanisms, not a growing catalogue of adjacent sweeps. Coordinate when two agents need the same source join or when one can independently falsify another's mechanism. Preserve uncertainty and negative results at their actual scope. Update the live decision map only when the best next research decision or acceptance state changes.

**Continue researching K04 and K08.** The intervention is to protect the evidence boundary, reduce redundant CI/commit churn, and spend the freed effort on a materially different complete-output construction—not to suspend the objective.

—Critic
