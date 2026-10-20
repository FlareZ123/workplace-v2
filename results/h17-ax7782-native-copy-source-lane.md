# AX-7782: an unrequested native archive-copy source lane, and its limits

**Agent 30, 20 October 2026 (normal research).** Objective: identify an original-target-bearing source class that has a concrete selector in the supplied archive and was absent from the current missing-evidence request. This is a records-custody retrieval hypothesis, **not** a seventh/eighth REC8 PASS.

## Direct original anchors

* `resources/evidence/mail/13.eml` identifies **AX-7782** as the *actual retained copy* of `IR-261003-H17`, distinguishes AX-7778 (drill), AX-7781 (dry run), and AX-7783 (stopped), and says Gabriel left a **handoff print** in the ordinary records folder. It explicitly states that the print contains the reference and receipt chain, **not the whole archive**.
* `resources/evidence/transfers/transfer-audit.jsonl` has **16 CHUNK attempts** for AX-7782, 2 per sequence 0..7, each reporting `bytes=1048576`, plus exactly one `COMMIT` with `dry_run=false`, `chunks=8`, object `IR-261003-H17`, and `receipt_utc=2026-10-03T20:55:10Z`. This describes an 8 MiB logical handoff (**8 × 1,048,576 = 8,388,608 bytes**) if the per-chunk sizes are truthful, **not 8 MiB actually present in the supplied export**. The eight selected highest-attempt checkpoint fields are `8947 CEDC B9CC 73BA B7E8 7BE6 3302 C5C9`.
* `resources/evidence/transfers/queue-note.txt` calls checkpoints **2-byte opaque fields**, with no documented content-hash algorithm. Thus they cannot be treated as a checksum proving independent archive bytes, reconstructed as missing ciphertext, or used to invert a 16-byte coupon.
* The local 46-file ZIP contains the transfer log/queue note but **no native AX-7782 chunk object, storage manifest or original handoff print**.

## New source-specific retrieval question

The existing intake emphasizes original ESC-N printer spool, Emily's final margin/photographs, the historical R-drive index and preserved desktop/print-host images. The **pre-fire retained native `AX-7782` transfer object and its original off-appliance handoff/receipt locator** constitute an additional, directly named original-source class. Under records-custodian authorization, ask only whether an **already-preserved offline copy** of the eight native chunks, the original signed handoff print, or the storage manifest/index identifying their historical location survives. Preserve these in read-only form with timestamps, media identity and actual provenance; do not access a live transfer service.

Before inspecting payloads, independently establish from those originals that the transfer was real, that `AX-7782` designates the H-17 incident archive and that any collected manifest corresponds to the selected committed transfer. Then inspect **unencrypted container headers, preservation catalogues, sidecar indexes or explicitly duplicated historical recovery records**, if present, for an independently original `PS-261003-0417` 18:02 attempt-2 RECOVER payload or Emily's exact final envelope caption. Such a record would be newly target-bearing and should undergo the existing `work/h17_witness_intake.py` provenance and unchanged verifier gate. If the obtained object is only encrypted archive bytes with no accessible independent metadata, **stop:** its existence cannot establish K04 or K08 without the key.

## Important chronology warning

The original MAIL-13 header is dated **2026-10-02 09:56 UTC**, but the transfer log's receipt is **2026-10-03 20:55:10 UTC**. A message written on 2 October could not contemporaneously witness a 3 October completed transfer as a past event. The same `receipt_utc` appears on different dry-run, drill, aborted and committed transfer records. That is a **source-level dating/provenance tension**, not a license to change the accepted K07 reduction or to assert fabrication. An independently dated historical signed handoff/manifest is required before trusting the transfer's claimed custody chronology.

## Distinctness and stop conditions

This lane is distinct from attempting to derive K04 by brute-forcing masked spool bytes, fitting MT19937 or using the tiny K07 checkpoints as donors. It targets the **original native object explicitly asserted to have been retained separately**, a possible information-bearing source beyond the given directory. Unlike an undirected device search, the original identifies the exact transfer ID, object identifier, declared chunk count and reported size.

**Measured target gain in the supplied material: K04 0/128 independently authenticated coupon bits; K08 0 attested exact final-caption words.** Six verified REC8 slots remain unchanged and combined recovery remains **INCOMPLETE**. No native transfer data has been received and nothing here certifies that the archive was readable without its lost recovery card.
