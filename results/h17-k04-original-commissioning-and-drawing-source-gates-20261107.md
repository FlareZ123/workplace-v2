# K04 primary commissioning and supplier-drawing source gates

**Status:** new source-acquisition leads; no coupon bytes recovered and no printer model asserted.

## 1. The route sheet is explicitly derivative

The supplied custodian note says the archive supplier's commissioning note names K01–K08 and that the **route sheet is a transcription of the commissioning reduction rules**. The supplied `recovery-routing.json` is the route sheet used by current analyses. The original supplier commissioning note itself is absent from the local export and is not named in the current acquisition list.

This matters because the selected PS-0417 RECOVER ACK2 payload reduced with the recorded K04 XOR mask fails the immutable K04 commitment, while MAIL-16 and the custodian note distinguish dispatch acknowledgement from payload/media correctness. The transcription may be complete and accurate, but that has not been compared against its primary source.

**Acquisition:** obtain the original supplier commissioning note and the exact source version used to transcribe `recovery-routing.json`, including every page, attachment, cover, revision/issue record, handwritten correction, worked example and distribution/custody record. Compare line-by-line for K04 route, attempt selector, copy/render/media stage, byte order and K08 envelope/normalization/version selection. Do not silently repair the JSON. If the original is demonstrably identical and contains no additional rule, close this path.

## 2. MAIL-16 identifies an old supplier drawing

MAIL-16 (2026-10-03 07:49Z) states that ESC-S is also shown on the **old supplier drawing**, while the September label transcription is current and an August service mapping should not be substituted. This is a direct locator to a primary hardware/route-history source. It may identify the actual printer/cassette model, ESC-N/ESC-S physical paths, the L-29/N parts and the physical meaning of the “catch” component. It does not establish any of those details until the drawing is seen.

**Acquisition:** obtain the old supplier drawing, all sheets/revisions/legend/part lists, issue date, model and serial references, title block, and custody. Obtain the September current label transcription and August mapping as separate version controls. Do not use the older mapping as the current route selector.

## 3. BX25-08 is a bounded candidate locator, not an identified drawing

Supplier reconciliation row RN-052 records `RISK / R1 / FILED / FA-17 / BX25/08` as a property-annex scan inward transfer. The supplied `BX25-08.pdf` is a one-page, 5,407-byte AES-256 encrypted PDF. Existing structural inspection found font resources, no embedded image XObject and one URI link annotation; its page stream, metadata strings and URI target remain encrypted. These facts are compatible with a text/vector folio or a link/index to another record, but do not identify its contents.

**Hypothesis:** BX25-08 may be the property-annex folio, an index/redirect, or the drawing itself associated with FA-17 and MAIL-16's old supplier drawing. The original Risk-desk paper key register is the authorized release route. Do not brute-force the four-position setting or probe an encrypted URI. After authorized release, preserve the encrypted original and hash, then inspect the visible folio/title block, metadata and URI target; compare to the H17-POL-17 renewal ledger, September cassette-return index and MAIL-16. If BX25-08 is unrelated, request the separate drawing by its actual title/reference.

## 4. Selected-job ticket neighbours are competing candidates

The current North L-29/N offset table has two live candidate neighbours for selected PS-0417:
- +304 → ST-113
- +300 → ST-117

Neither mapping is source-defined. The current request list names the five North tickets through ST-112 but does not explicitly request the original ST-113/ST-117 records. Request both as competing candidates from the September supplier index/ledger, including posted, unposted, voided, held, reversed and duplicate versions; account/folio; creation/settlement times; work-order attachments; carbonless copies and any explicit PTW/PS cross-reference. A ticket number alone is not proof of a printer-job join. The Critic's 7 November 11:22 direction assigns the +300 line to Agent8 and requires original paired-source validation before further offset computation.

## 5. Downstream print-host evidence

MAIL-16 says the selected ACK establishes dispatch, not media integrity. If an independently identified host is Windows, the original acquisition should preserve native spool data and metadata (.SPL/.SHD where applicable), PrintService/Admin and Operational EVTX, queue/port/driver/print-processor configuration, device-local job history and any retained media/output. Establish the host OS and queue mapping before requesting OS-specific artifacts. Preserve PS-0417 attempt 1/2/3 and the earlier LABEL event as controls. The physical ESC-N coupon or retained media requires its own chain of custody.

## Falsifiable outcome

These are source locators and acquisition gates, not a proposed byte transform. A complete original commissioning note identical to the JSON, an unrelated BX25-08 folio, or original index records assigning ST-113/ST-117 elsewhere should close the corresponding path. A drawing that identifies the model and physical output path, or a native spool/device record that binds PS-0417 ACK2 to the printed media, would materially advance the K04 copy-stage question.

No new K04 candidate is claimed.