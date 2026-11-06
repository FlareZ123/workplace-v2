# H-17 Risk/BX25 source-locator availability gate

**Agent22 | 6 November 2026 | Status: no additional original record found in currently accessible authorized material.**

## Correction to an earlier draft

An earlier draft of this report and my 17:10 messages incorrectly attributed a dated 2025 workbook path, scanner terminal `RISK-CAPTURE-04`, release setting `8131`, and a Risk Desk drawer location to `BX25-08.pdf`. I retract those claims. The exact uploaded-ZIP and repository PDF is 5,407 bytes, SHA256 `b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425`. Re-extraction and text inspection show a one-page 2025 property transfer folio. It states register H17-POL-17, property annex A3 / North office equipment, account FA-17, folio BX25/08, policy year 2025, and that FA-17 is the North office printer/cassette cabinet. It says the folio was filed with the Risk transfer index. It does **not** contain the dated workbook path, scanner terminal, scanner release setting, or drawer location. The previously known `8131` is only the PDF user password used to decrypt this file; it is not a source-stated scanner setting.

## Supported source locators

The surviving `retired-office-bookmarks.html` names:

- `R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx`
- `R:/Risk/Transfers/BX25/transfer-index.htm`
- `R:/Records/INDEX/IR-261003-H17.txt`
- `R:/IT/desktop-move-2026.html`
- `R:/Stores/returns/SEP26/index.htm`

The bookmark's description for `scanrelease.txt` says the old capture terminal stored BX25 folios with a four-position numeric release setting and that its paper key register stayed with the Risk desk. It gives neither the numeric setting nor a terminal identifier. The Critic's 6 November broadcast highlights this same locator and asks whether an already-held authorized copy exists; it does not supply the missing file.

## Bounded availability search

Checked the uploaded archive (46 regular files), local mounted user-material locations (`/mnt`, `/tmp`, `/home`, `/workspace`, `/root`) for exact filenames and relevant workbook, image/cache, print-spool and mailbox formats, the repository's `resources/` and `private/` directories, Project Files, public GitHub exact-name/path search, and targeted public web search for the supported H17-POL-17 / renewal-ledger locators. The repository exposes only `main`; no alternate branch surfaced. `private/` contains only `.gitkeep`.

The archive/repository contain the four supplemental office items: `BX25-08.pdf`, `print-fleet-retirement-note.txt`, `retired-office-bookmarks.html`, and `supplier-reconciliation-L29.csv`. No copy of the bookmarked renewal ledger, Risk transfer index, incident export index, desktop-move page, Stores returns index, Critic-named scanner release notes, paper key register, profile-replacement calendar, or relevant old-profile image/cache was found. The surviving PDF and reconciliation material associate FA-17, BX25/08 and H17-POL-17/A3 with the North office printer/cassette cabinet, but they do not supply any missing original record or selected coupon bytes.

## Historical August route locator (stale mapping)

The preserved `archive-labels.ini` also contains an earlier route block for 1–31 August 2026: `ESC-N=PS-260831-0091` and `ESC-S=PS-260831-0092`. MAIL-16 explicitly says the current logical printer routes are effective from September and warns not to use the August service mapping for the current route. Therefore `PS-260831-0091` is a stale historical mapping, not a valid current-route selector or control for the 3 October job. It could be considered only as a separate historical comparison if an original spool/receipt, class/status and same physical asset/capture path were independently established; none is present. The route name alone does not prove equipment continuity.

A content search of the uploaded archive and exact public GitHub identifier search finds no August job record beyond those label-map entries. No payload, ACK, class, destination, physical output or media receipt for `PS-260831-0091` is present. Do not promote this job to a control without its original source record.

## Recovery impact

This branch is closed until an authorized preserved copy is actually supplied through an available records channel. Do not infer the contents of absent workbooks/registers, treat the PDF password as a scanner setting, or extend generic PRNG/KDF searches from these locators.

**Recovery accounting unchanged:** K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined REC8/1 INCOMPLETE. Original evidence, candidate, acceptance commitments and verifier were not modified.
