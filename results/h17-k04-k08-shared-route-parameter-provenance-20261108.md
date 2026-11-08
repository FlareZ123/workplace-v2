# H-17 K04/K08: shared route-parameter provenance audit

**Date:** 2026-11-08  
**Researcher:** Agent 29  
**Status:** source-lineage finding; neither parameter independently validated  
**Question:** Do the K04 XOR mask and K08 desk nonce share an original source record, transcription event, version, or error path?

## Conclusion

The two exact 16-byte literals share a **secondary transcription container**: both appear in `resources/evidence/recovery-routing.json`. The records-custodian note explicitly describes the route sheet as a transcription of the commissioning reduction rules. The local export does **not** establish that the mask and nonce came from the same primary record, were transcribed by the same person, or share a specific revision. A common transcription error is possible, but there is no evidence to treat it as established or to alter both values together.

## Source-derived chain

### K04

- `recovery-routing.json` records source as “escrow coupon / logical printer route ESC-N”, with the mask literal `8556C8CB6140A7F9A5123AC7571BEE1C`.
- `MAIL-16` (Simon, 3 October, 07:49 UTC) independently says ESC-N is the north coupon used for the masked component, instructs use of the last acknowledged attempt for the exact job, and warns that ACK is a dispatch receipt rather than a media-integrity flag.
- `archive-labels.ini` independently maps ESC-N to `PS-261003-0417` for 1 September–3 October 2026. It also lists ESC-S and WATCH-SPARE. This corroborates the logical route/job selection, **not the 16-byte mask**.
- `archive-labels.ini` is the surviving label-route transcription. It contains no K04 mask and no K08 nonce.

### K08

- `recovery-routing.json` records source as “keeper's desk phrase, crew notes and noticeboard drafts”, with desk nonce `5F933DA6A1BD03C32DA5CBC25344F497`.
- `MAIL-20` (Gabriel, 4 October, 11:06 UTC) explicitly says Emily's normalization rule is on the route sheet, along with the desk nonce. It does not reproduce the nonce or provide an independent copy.
- The crew/noticeboard file contains drafts and standby/commissioning labels, but not the exact nonce or the final keeper phrase.
- The records-custodian note defines K08 as the keeper's personal desk phrase and says the route sheet is a transcription of the commissioning reduction rules.

### Shared transcription layer

- `MAIL-10` and `MAIL-18` also refer to the route sheet for the event/freeze window and recorder latch window. This is consistent with a common multi-slot commissioning-reduction sheet.
- `START_HERE.md` identifies this as export 06 prepared 4 October 2026 at 11:40 UTC, says the machine identifiers and hexadecimal recovery fields were retained as supplied, and states that the original mailboxes and devices are unavailable. This timestamps the export package, not the original route sheet, the parameter transcription event, or its author. The custodian note names Emily as custodian; it does not identify her as route-sheet transcriber.
- The exact K04 mask and K08 nonce occur in no other local source file as ASCII hex, spaced/colon/hyphen byte strings, raw 16-byte values, reversed bytes, reversed 32-bit words, or common per-word endian variants. The encrypted BX25 PDF was only included in this bounded raw-byte scan; no decryption or password guessing was attempted.
- The JSON has no `transcribed_by`, `created_at`, `revision`, source-page locator, or document hash. Git history has no earlier version to compare. ZIP timestamps are a common export-packaging timestamp and do not establish original document chronology.

## What is and is not independently supported

| Item | Independent local support | Still unverified |
|---|---|---|
| K04 ESC-N route and job identity | MAIL-16 and archive-labels.ini | Whether the mask literal matches the original coupon/commissioning record |
| K04 mask literal | Only recovery-routing.json | Original coupon or commissioning-note value |
| K08 normalization rule and nonce location | MAIL-20 says both are on the route sheet | Exact nonce literal against the original route sheet |
| K08 phrase | Crew drafts establish context and competing labels | Emily's author-final wording on the original envelope/desk carrier |

## Next source-bearing action

Request and preserve the **original commissioning reduction rules / route sheet with revision and custody metadata**, plus the **original ESC-N coupon / H17-POL-17/A3 card front and back**. Treat the K04 mask as a separate physical-coupon check. Separately request the **original desk route sheet** and the original envelope/desk carrier for K08. If a version history or a second transcription is recovered, compare the two 16-byte literals independently and record the transcriber, source page, revision, and timestamp.

Do not infer a shared error merely because the literals coexist in one JSON file. Do not change either parameter without an independent source witness.
