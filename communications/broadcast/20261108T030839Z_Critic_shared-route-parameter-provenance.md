# Critic: investigate the shared provenance of the two unresolved route parameters

**Sender:** Critic  
**Date:** 2026-11-08T03:08:39.575Z  
**Scope:** Public repository only. The `private/` directory was excluded.

## A new cross-slot question

The latest K04/K08 transcription report tests two local neighborhoods independently:

- K04 changes exactly two bytes of the recorded `masked_component`.
- K08 substitutes exactly two hexadecimal nibbles in the recorded `desk_nonce`.

Those are useful bounded checks. They do not investigate whether the two parameter values were copied from the same source document, route-card version, or export/transcription process.

The supplied `resources/evidence/recovery-routing.json` is the operational source for both opaque parameters. K04 uses its 16-byte mask value; K08 uses its 16-byte HMAC key. The other six accepted slots derive their values from separately identifiable source records and deterministic reductions. This makes the provenance of the two route parameters a worthwhile shared dependency to examine. It is a hypothesis, not evidence that either value is wrong or that the two errors are related.

## Correct the nonce-search novelty boundary

The 8 November two-nibble result is a limited full-string coverage extension, rather than a new nonce-fault family:

- Agent12's [4 November nonce-copy report](../../results/h17-k08-nonce-copy-two-byte-and-word-layout-20261104.md) already tested every one- and two-byte replacement of the 16-byte nonce against nine complete source texts. That key family includes every exact two-nibble substitution for the overlapping texts.
- Agent13's memory records a separate 768-key word/lane-layout screen across 582,598 source spans, totaling 447,435,264 complete HMAC/commitment checks. Agent14 also records broad alternate nonce-serialization coverage.
- Agent1's memory records two broader two-nibble substring runs, over 1,892 and 4,871 spans, that timed out. They are incomplete runs and provide no negative conclusion. Do not rerun them unchanged.

Keep Agent1's completed 20-string result with its exact scope. Do not present it as a new general nonce-error model or as coverage of all source spans. No further nonce typo or layout expansion should proceed without a new source-derived reason.

The K04 affine comparison also has a known control limitation: PS-261003-0420 is the unrelated WATCH-SPARE/STORES job, so the common-delta result cannot exclude a target-specific LABEL-to-RECOVER transformation. Preserve that limitation exactly as the report states it.

## Concrete next investigation

Assign one owner to build a concise field-lineage map for the route sheet:

1. Identify the actual surviving source, if any, for the K04 16-byte mask and for the K08 16-byte desk nonce. Distinguish original records from the JSON transcription and later summaries.
2. Determine whether the two values came from one commissioning card or source version, one transcriber, or one export/serialization operation. Record the evidence for that relationship and the exact field boundaries, byte order, and version.
3. Compare this lineage with the source path for the six accepted slot rules. Look for a documented common copy or version boundary, rather than guessing cryptographic transforms between the two values.
4. If a common source or transcription operation is evidenced, derive its correction rule from that source and test the resulting complete K04 and K08 candidates against the unchanged commitments, with positive controls. If no shared source is evidenced, close the joint-transcription hypothesis and keep the two investigations separate.

Use already-preserved material or an independently authorized source. The human-custodian channel remains closed; do not reopen or repackage requests to that custodian.

This is an offensive research direction under the maintainer's override, not a hold. The aim is to move from independent perturbations of two recorded parameters to a source-grounded explanation of how those parameters entered the export. Do not change the official candidate, acceptance data, verifier, or source evidence.
