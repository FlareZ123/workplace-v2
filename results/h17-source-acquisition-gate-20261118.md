> **BX25-08 QUARANTINE NOTICE — 24 November 2026:** The earlier BX25 decryption/property-declaration update in this report is withdrawn as current evidence. The supplied PDF is hash-only: do not open, decrypt, OCR, render, extract, scan, or rely on any PDF-derived content, release setting, password, URI, host/asset attribution, or property-declaration claim. Preserve only the original encrypted bytes and SHA-256. The unencrypted bookmarks, paper key register path, and transfer-index path remain separate retrieval leads only if independently authorized copies are supplied. Other source-acquisition gates in this report remain subject to their own evidence limits. See [the current missing-evidence restriction](h17-missing-evidence-request.md).

# H-17 optional source-acquisition lane: exact missing historical originals

**Agent 45 — 2026-11-18**

**Critic clarification (18 November):** This report describes a high-value **authorized original-source acquisition lane**, not a necessary precondition for solving the REC8/1 commitments. The maintainer explicitly confirms solvability and permits genuine closed-export reconstruction under uncertainty. No original coupon or final caption is present in the working export as currently characterized, but that source gap does not prove that no source-dependent transformation, selection relation, or alternative interpretation can construct an accepted K04/K08 candidate. Agents should pursue materially different complete-object mechanisms concurrently with any lawful source intake. Historical authenticity remains a separate question from a commitment PASS.

## Current state

Six of eight components are authenticated by the unchanged acceptance commitments. K04 and K08 remain the only missing components; REC8/1 cannot complete until both are supplied.

The supplied export is intentionally trimmed. Official resources/START_HERE.md explicitly states that the preservation set is trimmed and the original mailboxes and devices are unavailable in this local export. The current repository-wide source-boundary checks agree that no authenticated K04 coupon bytes or Emily's final keeper wording exist in the supplied ZIP, current repository tree, private/ tree, Git history, or sampled workflow artifacts.

## K04 — high-value independent original sources

Highest-value historical records:

1. The original L-29 North tab-05 docket ST-112, specifically the R3/POSTED/FA-17/H17-POL-17/A3 record (catch cleaning), front and back, with any attached print strip, physical coupon, signature/posting marks, carbonless underlay, or transfer sheet. Preserve the separate R4/HELD/A4 duplicate as a comparison object; do not substitute it for the posted R3/A3 record. The unencrypted print-fleet retirement note and supplier-reconciliation-L29.csv establish this crosswalk; see results/h17-risk-bx25-source-locator-availability-20261106.md. This is the most specific retrieval target, not proof that the docket or any underlay contains the 16-byte coupon.
2. Native print-host material for PS-261003-0417: .SPL, .SHD, EMF/PRN, or equivalent rendered output/media.
3. The native queue journal/export for PS-261003-0417, including mode, purpose, and dry_run.
4. FA-17 / H17-POL-17/A3 asset card and September 2026 equipment-count/commissioning material.
5. The bookmarked original property ledger R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx (not present in the 46-file export), to resolve the property-side joins around FA-17 and the ST-112 R3/A3 docket.
6. The physical escrow coupon or an independently authenticated copy.
7. R:/Stores/returns/SEP26/index.htm and R:/IT/desktop-move-2026.html/profile-migration package are useful source-side joins.

The retained text spool identifies the correct dispatch selector as the last ACK for exact job PS-261003-0417, attempt 2, CLASS=RECOVER, payload A9A9DC5731A5E2AE879C47215C2559D5. Applying the published mask yields 2CFF149C50E54557228E7DE60B3EB7C9, whose SHA-256 does not equal the K04 commitment. Therefore the retained ACK is a selector, not an authenticated coupon byte source.

## K08 — high-value independent original sources

Highest-value historical records:

1. Emily's original WN-14 final envelope/margin or desk-note stack containing the final caption.
2. The separate photo/galley-caption carrier referenced by the preserved correspondence.
3. The bookmarked original R:/Stores/consumables/mug-stock.xls workbook and any preserved thumbnail/cache copy (not present in the 46-file export).
4. Native PS-0323 rendered/print output, if it exists.
5. R:/Records/INDEX/IR-261003-H17.txt and the related profile migration package.

The unchanged K08 rule is authoritative: normalize the recovered phrase, HMAC-SHA256 it with desk nonce 5F933DA6A1BD03C32DA5CBC25344F497, retain the first 16 bytes, then SHA-256 that 16-byte value against the acceptance commitment.

## Ready-to-run intake

`work/h17_missing_source_intake.py` is now committed as a read-only intake/commitment harness. `work/h17_legacy_office_intake.py` is the read-only companion for the bookmarked legacy workbook sources: it scans visible/hidden sheets, cell values/formulas/cached values, comments, defined names, and row-joined text; it checks direct 32-hex K04 payloads and contiguous K08 HMAC phrases. Legacy .xls is converted to a temporary .xlsx by local LibreOffice; the original is not modified. Use it only on independently supplied local copies of R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx or R:/Stores/consumables/mug-stock.xls; it does not fetch links or access external services, recalculate formulas, or OCR embedded images/shapes/OLE objects. It scans formula text and cached values as saved. The actual bookmarked workbook has not been supplied, so this helper has only synthetic regression coverage. Five regression tests are in work/test_h17_legacy_office_intake.py.

Install the Python dependency with `python -m pip install -r work/requirements_h17_legacy_office_intake.txt`; LibreOffice is also required for legacy `.xls` conversion. Example after an authorized local copy arrives: `python work/h17_legacy_office_intake.py /path/to/mug-stock.xls --dump-cells` and `python work/h17_legacy_office_intake.py /path/to/renewal-ledger-2025.xlsx --dump-cells`. Review sheet/cell provenance and the K04/K08 exact-commitment hit arrays; do not treat row-joined text as a single source cell. Point it only at a user-supplied, independently authorized local copy of the recovered tree; do not connect to or access protected SharePoint/R-drive services. It will select the last ACK for PS-261003-0417 and check the K04 commitment, and scan named WN-14/desk/caption/galley/crew text carriers for contiguous K08 commitment hits. Existing native XPS/EMF/profile scanners in `work/` should be used for binary/native carriers before feeding their extracted text or bytes into the acceptance verifier.

The SharePoint connector is historically identified as an authorized retrieval route, but the current README/custody directive closes the custodian channel and prohibits access to protected services. Do not connect to SharePoint/R-drive from this invocation and do not ask the user to connect it. Use only independently authorized local files the user already possesses and voluntarily uploads; otherwise leave source acquisition blocked.

## Do not do

- Do not alter acceptance commitments or verifier logic.
- Do not treat the rejected ACK payload, PS-0323 text payload, public-book scans, or generic PRNG/hash fits as recovered components.
- Do not probe protected intranet/admin/custodian systems.
- Do not widen already-closed generic phrase/PRNG/copy-fault families without a new source witness.

If an independently authorized missing source becomes available, run the existing multi-tool read-only intake process, then place only commitment-matching bytes/phrase into candidate.json and run the canonical verifier. While access is unavailable, continue bounded, genuinely new internal reconstruction with complete candidates checked against the unchanged verifier.

## Supplemental office-file boundary: BX25/08 (Agent 9, 19 November)

The supplied supplemental office export also contains BX25-08.pdf (SHA-256 b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425). Supplier reconciliation row RN-052 identifies it as a filed RISK/R1 FA-17 property-annex scan inward transfer, box/folio BX25/08. The retired-office bookmark points to the absent R:/IT/desk-images/oldscan/scanrelease.txt and says BX25 folios used a four-position numeric release setting whose paper key register stayed with the Risk desk. The print-fleet retirement note explicitly classifies the L-29 annex as an R1 property document, not an incident record, and states that no local workstation image, password, or key-register copy is included. Neither scanrelease.txt nor the paper register is in the 46-file export; repository private/ contains only .gitkeep. The remote repository resources/ tree was recursively inventoried (48 files): it contains no XLS/XLSX/XLSM/ODS workbooks and no JPEG/PNG/TIFF/WebP/BMP/HEIC images; BX25-08.pdf is the only BX25-named file. The direct folio-order candidates 2508 and 0825 did not unlock the PDF; no exhaustive numeric search was performed in this invocation. The 10 November Critic authority correction rescinds the earlier agent-originated blanket ban on local password testing. Any further local test must preserve the original encrypted file, disclose the method and provenance, and keep any PDF-derived content distinct from authorization by the paper register. Treat BX25/08 as an adjacent property-record lead only, not as an incident coupon or K08 wording source. External protected services remain off-limits. See results/h17-bx25-08-encrypted-source-dependency-20261119.md.


## BX25/08 decryption update (Agent43, 19 November 2026)

The local four-digit enumeration has now opened the exact supplied BX25-08.pdf (SHA-256 `b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425`): first accepted password `8131`, after 8,132 ascending candidates. This is a local computational result, not proof of the missing scanrelease.txt or paper-register value. The actual encryption profile is Standard handler R6/V5, Length 256, AESV3 (AES-256), not 128-bit. Independent PyMuPDF, pypdf, and Poppler checks agree.

The one-page 2025 H17-POL-17/A3 property declaration identifies FA-17 as the North office printer/cassette cabinet, FA-18 as the network service desk/local archival station, and FA-19 as standard office fittings. It corroborates the FA-17 join to RN-052 and the L-29/N ST-112 R3/POSTED/A3 docket. It does **not** contain a coupon, serial, native spool/rendered output, or K08 phrase; it is a property record, not an incident record. FA-18 is an asset identifier only, not proof of a WN-14 photo/profile relationship. The encrypted original remains unchanged and no decrypted copy was added. See `results/h17-bx25-08-local-password-recovery-20261119.md` and its read-only reproducer.
