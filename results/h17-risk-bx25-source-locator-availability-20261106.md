# H-17 Risk/BX25 source-locator availability gate

**Agent22 | 6 November 2026 | Status: unavailable in currently accessible authorized material.**

## Why this check was opened

The surviving `retired-office-bookmarks.html` names the original Risk paths:

- `R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx`
- `R:/Risk/Transfers/BX25/transfer-index.htm`
- `R:/Records/INDEX/IR-261003-H17.txt`
- `R:/IT/desktop-move-2026.html`

The Critic's 6 November locator adds `R:/IT/desk-images/oldscan/scanrelease.txt`, the Risk desk paper key register and the profile-replacement calendar. The unlocked `BX25-08.pdf` contributes a second exact source workbook path: `R:\Risk\Renewals\H17-POL-17\schedule\2025-08-14.xlsx`. Its own text identifies scan terminal `RISK-CAPTURE-04`, release setting `8131`, and paper key register `Risk Desk / drawer 2`.

## Bounded availability search

Checked the original uploaded archive (46 regular files), all mounted user-material locations available in this runtime (`/mnt`, `/tmp`, `/home`, `/workspace`, `/root`), the repository's complete `resources/` and `private/` directory listings, public GitHub code search for the exact filenames and paths, and targeted public web search for the ledger/workbook identifiers. The repository exposes only `main`; no alternate branch surfaced. `private/` contains only `.gitkeep`.

The archive and repository contain the four known supplemental office items: `BX25-08.pdf`, `print-fleet-retirement-note.txt`, `retired-office-bookmarks.html`, and `supplier-reconciliation-L29.csv`. The PDF is the 2025 one-page transfer folio; it does not contain its source workbook as an attachment. No copy of the Risk transfer index, renewal ledger, dated source workbook, scanner release notes, paper key register, incident export index, desktop-move page, profile-replacement calendar, or relevant old-profile image/cache was found. Public GitHub/web search results expose locator references and research notes, not the missing original records.

## Evidentiary boundary

The available PDF and reconciliation material make the locator plausible: they associate FA-17, BX25/08 and H17-POL-17/A3 with the North office printer/cassette cabinet and the Risk desk. They do **not** authenticate the contents of any absent workbook, connect that workbook to the 3 October selected ESC-N coupon, or supply coupon bytes. The known `8131` PDF user password is not evidence that it is the printer's seed or the selected coupon.

This branch is closed until an authorized preserved copy is actually supplied through an available records channel. Do not launch a PIN sweep, infer the missing ledger contents, or extend generic PRNG/KDF searches from the locator alone.

**Recovery accounting unchanged:** K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined REC8/1 INCOMPLETE. Original evidence, candidate, acceptance commitments and verifier were not modified.


## Additional same-route control locator found during the handoff review

The preserved `archive-labels.ini` also contains an earlier route block for 1–31 August 2026: `ESC-N=PS-260831-0091` and `ESC-S=PS-260831-0092`. This is an exact prior ESC-N job identifier and could become a route-matched historical control **only if** an original spool/receipt or attributable physical output is found and its class/status are established.

A content search of the uploaded archive and exact public GitHub identifier search finds no August job record beyond those two label-map entries. No payload, ACK, class, destination, physical output or media receipt for `PS-260831-0091` is present. The route-map entry is a locator, not evidence that the August job was RECOVER or that its bytes validate the October selected route. Agents38 and 32 were notified. Do not promote this job to a control without its original source record.
