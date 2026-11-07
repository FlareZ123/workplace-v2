# BX25-08 property annex recovered (7 November 2026)

## Recovery

The supplied `BX25-08.pdf` was encrypted with AES-256 (PDF V=5, R=6). The retired-profile bookmark explicitly states that BX25 scan folios used a four-position numeric release setting. A bounded search of that four-digit space recovered a valid release setting; the value is preserved in `private/bx25-08-release-setting.md`, not repeated here.

The decrypted PDF contains one page. The extracted text is preserved below in source order.

## Source transcription

```text
RISK DESK - ANNUAL PROPERTY DECLARATION
TRANSFER COPY  /  2025
Register:
H17-POL-17
Property annex:
A3 - North office equipment
Account reference:
FA-17
Inward scan folio:
BX25/08
Policy year:
01 Jan 2025 - 31 Dec 2025
SCHEDULE ACCOUNT HOLDER / NAMED INSURED
Noyes Energy Group
Operating company - H-17 Atlantic facility
Declared office-property carry-forward
FA-17     North office printer / cassette cabinet              carry-forward: maintained
FA-18     Network service desk and local archival station      carry-forward: maintained
FA-19     Standard office fittings                          carry-forward: maintained
Renewal review: recorded 18 Nov 2025 / Property team copy
Filed with Risk transfer index, folio BX25/08.
Legacy desk-scan export. Index dates reflect the archive transfer cycle.
H-17 / RISK / BOX 25 / FOLIO 08
1 of 1
CORPORATE RECORDS / CORRESPONDENCE
Electronic correspondence index: https://noyes-energy-group.pages.dev/
Policy file H17-POL-17/A3  |  Transfer folio BX25/08
```

## Evidence implications

1. **K04 route lineage:** A3 / H17-POL-17 / FA-17 is explicitly the North office printer and cassette cabinet. This corroborates the FA-17 mapping in the 4 October print-fleet return register. It does not by itself prove the logical ESC-N route at the incident instant or validate the retained spool payload.
2. **K08 scan lineage:** FA-18 is explicitly the network service desk and local archival station. This corroborates the retired-office bookmark's `R:/IT/desk-images/oldscan/` path as belonging to the archival workstation.
3. **2025 source limitation:** This is a transfer copy of the A3 property annex, not the original `renewal-ledger-2025.xlsx`, scan-release notes, paper key register or complete incident desk export index.
4. **External-link boundary:** The PDF labels `https://noyes-energy-group.pages.dev/` as the electronic correspondence index. The public root is a corporate marketing site; `robots.txt` disallows `/admin` and `/api/`, and `/admin/` is a username/password portal posting to `/api/login`. No credentials or forms were submitted. This is not an accessible correspondence index; the actual export must come from the records custodian. The PDF release setting must not be reused as a website login credential. See [Noyes portal boundary report](h17-noyes-correspondence-index-portal-boundary-20261107.md).

## Current status

The annex resolves the asset descriptions and strengthens the source chain for both K04 and K08. It does not provide the missing 16-byte K04 coupon, the five Part I book pages, or the K08 final caption. No acceptance slot has been marked PASS on the basis of this PDF alone.
