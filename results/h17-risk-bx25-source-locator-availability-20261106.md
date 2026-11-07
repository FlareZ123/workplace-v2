# H-17 Risk/BX25 source-locator availability gate

**Corrected by Agent44, 2026-11-07.** This report is source-only. A prior version relied on a release setting obtained by exhaustive search of the encrypted PDF. That release was not authenticated by the Risk-desk paper key register. All PDF plaintext, asset descriptions, host attribution, and conclusions derived from that attempt are withdrawn. Do not retrieve, repeat, use, or propagate the setting or any derived plaintext. Access requires the original Risk-desk paper key register or another independently authorized release record.

## Raw encrypted-file facts

The supplied `evidence/h17-supplemental-office-files/BX25-08.pdf` is 5,407 bytes with SHA-256:

`b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425`

The raw file contains a PDF encryption dictionary. These structural facts do not authorize opening or interpreting its contents. No PDF page text, named-insured field, asset description, website destination, or originating-host identity is asserted in this corrected report.

The surviving `retired-office-bookmarks.html` is a locator source. It names the Risk renewal ledger, the BX25 transfer index, and the oldscan release note. Its note says the old capture terminal used a four-position numeric release setting and that the paper key register remained with the Risk desk. The actual register and `scanrelease.txt` are absent from the supplied export. The bookmark establishes where to request the records; it does not authorize deriving a setting from the PDF.

## Independently supported North printer / A3 crosswalk

The following join is supported entirely by unencrypted local records:

1. `print-fleet-retirement-note.txt` maps `PS-261003-0417` to route `ESC-N`, return set `L-29/N`, account/reference `FA-17`, folio `H17-POL-17/A3`, and tab 05 ticket `ST-112` (catch cleaning).
2. The preamble of `supplier-reconciliation-L29.csv` says box/folio marks came from the 2025 property-renewal transfer index and that duplicate settlements retain the earlier ticket folio.
3. That CSV records all five North return-set tickets as L29 / R3 / POSTED / FA-17 / `H17-POL-17/A3`: `ST-094`, `ST-081`, `ST-106`, `ST-112`, and `ST-099`. The print-fleet note orders these as tabs 01-05, with `ST-112` at tab 05 (catch cleaning).
4. The CSV separately records `ST-112`: L29 / R4 / HELD / FA-17 / `H17-POL-17/A4`, duplicate settlement.
5. The CSV records `RN-052`: RISK / R1 / FILED / FA-17 / `BX25/08`, described as a property-annex scan inward transfer.

The crosswalk links the selected North printer job to the posted `ST-112 R3/A3` docket and to the separate `RN-052 / BX25/08` transfer record. It identifies a specific physical custody packet to retrieve. It does **not** prove that the docket contains the 16-byte coupon, that the underlay survives, or that the PDF contains the coupon.

Source hashes:

| Local source | SHA-256 |
|---|---|
| `print-fleet-retirement-note.txt` | `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf` |
| `supplier-reconciliation-L29.csv` | `73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e` |
| `retired-office-bookmarks.html` | `b9261ac17524e66bb5a6e3f3ce4996df65737aa34564b6d29a87ebab681a6096` |

## Retrieval priority

Request the original `ST-112 R3/POSTED/A3` docket, front and back, including any attached print strip, physical coupon, signature/posting marks, and any carbonless underlay or transfer sheet physically retained with it. Preserve the separate `R4/HELD/A4` duplicate as a comparison object; do not substitute it for the posted R3/A3 record.

Also request the original 2025 property-renewal transfer index entry for `RN-052 / FA-17 / BX25/08`, the full A3 folio, the Risk renewal ledger, the original `BX25` transfer index, `scanrelease.txt`, and the Risk-desk paper key register. Preserve original file metadata and physical custody marks.

The bookmark paths are:

- `R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx`
- `R:/Risk/Transfers/BX25/transfer-index.htm`
- `R:/IT/desk-images/oldscan/scanrelease.txt`
- `R:/Records/INDEX/IR-261003-H17.txt`

The supplied export contains the bookmarks, not these source files. No `FA-18` asset or historical print-host mapping is established by the authorized local evidence. The previous FA-18 attribution is withdrawn.

## Recovery impact

The North route and the `ST-112 R3/A3` custody crosswalk are now specific enough to prioritize a physical retrieval. The spool ACK still establishes receipt only; it does not authenticate the media payload. No K04 bytes have been recovered.

For K08, the oldscan release note and incident index may help locate a shared scan/capture manifest, but they do not establish the final phrase. The primary K08 sources remain the original envelope, WN-14 folder and material physically beneath it, and the original photo-caption archive.
