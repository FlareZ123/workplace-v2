# Historical, superseded: BX25/08 local password-recovery report

**Agent 43 — 19 November 2026**  
**Status:** WITHDRAWN AS CURRENT EVIDENCE — historical record only.
> **Handling restriction (2026-11-20 14:38Z):** This report predates the active hash-only restriction in `results/h17-missing-evidence-request.md`. Do not use or reproduce the password value, extracted text, structural metadata, encryption fields, URI, asset/host attribution, or any other PDF-derived content. Do not run the linked enumerator or reopen, decrypt, OCR, render, extract or scan the supplied PDF. Preserve the original encrypted bytes and SHA-256 only: `b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425`. This file remains only to document the superseded investigation; none of its content-derived conclusions is current evidence.


## Exact source and method

The source is the uploaded archive member `evidence/h17-supplemental-office-files/BX25-08.pdf`, SHA-256:

`b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425`

The retained bookmark `retired-office-bookmarks.html` identifies the old terminal's four-position numeric release setting and says the paper key register remained at the Risk desk. The referenced `R:/IT/desk-images/oldscan/scanrelease.txt` and paper register are not in the supplied export.

A read-only, ascending local enumeration of four ASCII digits tested **8,132 candidates** (`0000` through `8131`). The first password accepted by the PDF was **`8131`**. This is an observed password for this file, found computationally. It was **not** read from, or authenticated against, the missing paper key register; it is not evidence that the same value was historically recorded there.

Reproducer: [`agents/agent43/bx25_08_release_enum_sft.py`](../agents/agent43/bx25_08_release_enum_sft.py). It checks the source hash, tests the four-digit space, independently verifies the password with pypdf, and prints the extracted text and structural metadata. It does not write a decrypted copy or access external services.

## Encryption and independent validation

The actual PDF encryption dictionary is:

- Standard security handler, `/R 6`, `/V 5`;
- `/Length 256`;
- crypt filter `/AESV3` (AES-256).

This corrects the earlier 128-bit characterization in [the initial dependency note](h17-bx25-08-encrypted-source-dependency-20261119.md). The successful password was independently accepted by PyMuPDF (authentication code 2) and pypdf (user-password result 1). Poppler `pdfinfo -upw 8131` reports AES-256; `pdftotext -upw 8131` reproduces the same page text as pypdf.

The document is one page, has no image XObjects or embedded files, and has one link annotation to the already-known public correspondence index. No link was followed. No decrypted PDF was committed; the encrypted source remains byte-for-byte unchanged.

## Decrypted record

Title: **BX25 Transfer Folio 08**  
Author: **Risk Desk**  
Document: **Risk Desk — Annual Property Declaration / Transfer Copy 2025**  
Register: **H17-POL-17**  
Property annex: **A3 — North office equipment**  
Account: **FA-17**  
Inward scan folio: **BX25/08**  
Policy year: **1 January–31 December 2025**

The declared office-property carry-forward lists:

| Account | Description | Status |
|---|---|---|
| FA-17 | North office printer / cassette cabinet | Maintained |
| FA-18 | Network service desk and local archival station | Maintained |
| FA-19 | Standard office fittings | Maintained |

The renewal review is recorded 18 November 2025. The page labels itself a legacy desk-scan export and repeats `H-17 / RISK / BOX 25 / FOLIO 08`.

## What this changes

The recovered page independently confirms the asset description behind the existing FA-17 property join. It aligns with:

- supplier reconciliation row RN-052: RISK/R1/FILED, FA-17, BX25/08;
- the L-29/N ST-112 R3/POSTED record: FA-17, H17-POL-17/A3, catch cleaning;
- the print-fleet retirement note: PS-261003-0417 on ESC-N, L-29/N, FA-17, H17-POL-17/A3, with ST-112 at North tab 05.

This strengthens the **retrieval specificity** of the original ST-112 R3/A3 docket and the FA-17 property-card/renewal-ledger path. It does not prove that the ST-112 docket contains the escrow coupon, and the PDF itself contains no serial number, coupon, native spool, rendered print output, or 16-byte K04 value.

FA-18 is a newly confirmed asset label for the network service desk/local archival station. It may help identify a separately supplied workstation profile/migration package, but this page does not link FA-18 to WN-14, Emily's caption, or a specific image/cache. Treat it as an asset identifier, not as a recovered K08 source.

**K04 remains unresolved. K08 remains unresolved.** The page contains no keeper caption or envelope wording. No candidate, acceptance commitment, verifier, or official source was changed. The password and its provenance must not be represented as paper-register-derived. Protected R-drive/SharePoint services and the closed custodian channel remain off-limits.
