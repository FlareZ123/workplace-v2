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

<badge>All steps passed</badge>

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

If an authorized original AX-7782/Bundle06 object is supplied, run `work/h17_ax7782_joint_intake.py` against that object and the repository `resources/` directory, preserve its JSON report and input hash, and inspect only source-bearing artifacts actually present. Do not add another extractor or CI workflow merely to test an intermediate assertion.
