# H-17 Office and SQLite intake regression — 20 November 2026

## Question

Do the newly integrated read-only intake paths for legacy Word documents, legacy Excel workbooks, and Windows Sticky Notes databases execute together in repository context while preserving source bytes?

## Method

Extended the existing manual workflow `.github/workflows/agent31-xls-embedded-image-intake.yml` rather than adding another workflow. The workflow installs LibreOffice Calc/Writer plus the Python dependencies, compiles the adapters, and runs these existing test modules:

- `work.test_h17_doc_lo_fallback`
- `work.test_h17_xls_lo_fallback`
- `work.test_h17_ax7782_k08_sqlite_bridge`
- `work.test_h17_ax7782_joint_intake`
- `work.test_h17_sticky_notes_intake`

GitHub Actions run: [44676196662](https://github.com/FlareZ123/workplace-v2/actions/runs/44676196662)  
Workflow commit: `c853e7ab9746c22ab287361dc916a4ca35821759`

## Result

**Result: PASS — all workflow steps completed successfully.**

The workflow completed successfully. Compilation and the combined unittest command both exited successfully.

The synthetic regression coverage includes:

- Legacy `.doc` conversion preserving Word margin comments.
- Legacy `.xls` extraction of ordered cells, comments, hidden sheets, cached formula values, named ranges, cell style metadata, and explicitly anchored embedded image bytes.
- Nested-archive discovery of a named `plum.sqlite` database and adjacent WAL/SHM sidecars, including recovery of deleted note text retained in WAL.
- Read-only Sticky Notes extraction using verified temporary snapshots and raw WAL text carving.
- Joint intake orchestration across the existing transfer, K04 binary-window, and K08 phrase/SQLite tools, including source-hash preservation.

## Limits

These are synthetic fixtures. The passing tests validate adapter behavior, not the contents of the missing AX-7782 object. They do **not** establish that the real object contains a legacy Word file, legacy Excel workbook, Sticky Notes database, WAL, SHM, or any particular K04/K08 evidence. No K04 or K08 component was recovered by this test run.

The joint intake remains a read-only tool for an authorized local copy of the original object. Encrypted PDFs are not password-guessed by the intake path.

## Next use

From the repository root, run the joint intake on an authorized original object:

```bash
python work/h17_ax7782_joint_intake.py \
  --object /path/to/authorized-AX-7782-object \
  --resources resources \
  --transfer AX-7782 \
  --json-out /path/outside-repo/ax7782-intake.json
```

The JSON output must be outside the `resources/` tree and must not overwrite the source object. The tool hashes the input before and after and fails if the source changes. Add `--ocr` only when required and supported. Supply `--pdf-password` only if the password is independently provided through an authorized source; the tool never guesses it.

If intake identifies a candidate coupon or exact final caption, keep the **unmodified original** and a separate exact transcription. Then use the existing witness/acceptance gate from the repository root:

```bash
# K04: coupon-transcript.json contains job, attempt, state, class,
# timestamp_utc and the exact 16-byte payload_hex.
python work/h17_witness_intake.py \
  --coupon /path/to/coupon-transcript.json \
  --coupon-original /path/to/unmodified-coupon-source

# K08: final-caption.txt is the verbatim UTF-8 wording.
python work/h17_witness_intake.py \
  --caption /path/to/final-caption.txt \
  --caption-original /path/to/unmodified-envelope-or-note-source
```

The witness tool checks the original route/ACK selector and unchanged acceptance commitments. It records separate original-source and transcription hashes, but explicitly reports that a hash alone does not establish historical authenticity; custody and source provenance remain a human evidence requirement. It emits a complete candidate only when all eight slots and the combined commitment pass.

Inspect only source-bearing artifacts actually present in the acquired object. Do not add another extractor or CI workflow merely to test an intermediate assertion.


## Re-run after joint SQLite integration — 2026-11-20 06:30Z

Triggered the existing manual workflow again against the current main-branch head after the SQLite/WAL bridge was integrated into the joint-intake orchestrator.

- GitHub Actions run: [44688309333](https://github.com/FlareZ123/workplace-v2/actions/runs/44688309333)
- Tested head: `478b98b88bbf81f6555dda86dff10f6a32b6f72c`
- Conclusion: **SUCCESS** (completed 06:31:33Z).

This re-run exercises the existing DOC, XLS, SQLite/WAL, joint-intake and Sticky Notes regression modules plus the frozen teal-image synthetic positive/negative controls. It validates the current integrated code path; it does not establish that the absent AX-7782 object contains any of these file types, and it recovers no K04/K08 component. No candidate, acceptance, verifier, or source data was modified.
