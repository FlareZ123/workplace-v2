# H-17 retrieval checklist for the missing two components

**Current custody constraint:** Do not access protected SharePoint/R-drive services and do not recontact the custodian. This is a checklist only for records already independently authorized and supplied as local files by the user. Do not ask the user to connect protected services. If no such local copy is available, leave source acquisition blocked. Do not substitute public web pages or paraphrases.

If an independently authorized local copy is supplied, search these exact historical paths/names first.

## K04 / ESC-N

The local BX25-08 property declaration visibly bridges policy file `H17-POL-17/A3` to transfer folio `BX25/08` and identifies the North office printer/cassette cabinet. It is a 2025 property declaration, not an incident record or coupon. The locally recovered PDF password `8131` is not authenticated against the absent `scanrelease.txt` and is not the K04 component. See `results/h17-k04-bx25-risk-folio-bridge-20261120.md`.

1. `R:/Stores/returns/SEP26/index.htm`
2. `R:/Records/INDEX/IR-261003-H17.txt`
3. FA-17 / H17-POL-17/A3 asset card and September 2026 equipment-count / commissioning material
4. Native queue journal for `PS-261003-0417` with mode, purpose, dry_run, attempt, state, class, destination, and payload
5. Native print/rendered files for `PS-261003-0417`: `.SPL`, `.SHD`, `.EMF`, `.PRN`, or equivalent
   - Where the historical connection points to a print server, include the archived server-side queue/spool directory and journal as well as any client-side spool copy. Record the host and original path for each `.SPL`/`.SHD`; do not assume a workstation copy is authoritative.
   - For `.SHD`, `work/h17_shd_triage.py` provides offset-preserving ASCII/UTF-16LE ASCII-subset string triage only; it is not a structural parser and cannot authenticate job/document fields without the native queue/job manifest.
   - Preserve the complete job metadata (document name, datatype, print processor, port, user, DEVMODE, and page/output descriptors) plus all native text/image streams; do not reduce the source to the 16-byte dispatch payload. A possible PS-0417 joint K04/K08 carrier is an unverified hypothesis, not a current finding.
6. Risk-desk paper key register entry for the linked `BX25/08` / `H17-POL-17/A3` folio, including any coupon code, folio sidecar, release-setting index and paper-to-scan cross-reference. The local BX25-08 PDF explicitly links policy file H17-POL-17/A3 to transfer folio BX25/08 and declares the North office printer/cassette cabinet; it is a property declaration, not the coupon.
7. Physical escrow/recovery coupon or an authenticated scan/photo
8. `R:/IT/desktop-move-2026.html` and its profile-migration package

For the exact job, retain every record for `PS-261003-0417`; the published selector is the last ACK for that exact job. Do not substitute a REQUESTED row or the 16:45 LABEL row. MAIL-04 explicitly says a stores picking ticket is not the as-left record; do not use ST-112/ticket-suffix arithmetic as a foreign key to PS-0417. The ESC-N job selection must be supported by the route record and native job/host evidence, not the ticket offset.

## K08 / keeper desk phrase

1. Original ordinary WN-14 night-folder and underlay (loose desk leaves), including Emily's N23 page, final-margin note stack, and the physical recovery envelope `H17-IR-261003`. Preserve the envelope's faces, flap/seal, adhesive, folds, inserts, handwriting and original placement; preserve the N23 page front/back, full margins, handwriting, page order, inserts/underlays, folds, labels, pencil and removed sticker. Photograph the assembly before separation and keep it distinct from the signed WN-14 controlled-copy sleeve. Before any physical/indentation examination, preserve custody and high-resolution images of all faces/edges; do not erase, clean, or apply ESDA first. Any later ESDA should follow the [qualified underleaf-indentation recovery path](../results/h17-k08-underleaf-indentation-recovery-path.md). The physical identity gate is a retrieval aid, not proof that any particular leaf contains the final phrase.
2. Original photo-caption carrier referenced by MAIL-11/MAIL-20
   - Include the PTW-417 cosmetic-corrosion photograph requested in MAIL-04 / `maintenance/work-order-417.html`, with its original image bytes, caption/sidecar, timestamps and revision history. It may or may not be the N14 sunrise photograph; treat that association as a retrieval lead, not an established identity.
3. `mug-stock.xls` or any preserved workbook/thumbnail/cache copy
   - Preserve native workbook bytes and all sheets, hidden sheets, formulas, comments, named ranges, cell metadata, drawing/VML/OfficeArt objects, floating images and alt text, hyperlinks, custom properties, revisions, autosave/thumbnail/cache copies. Retain the M10 cell anchor and any image overlapping it; do not convert to CSV/PDF before extraction.
4. Native `PS-261003-0323` output/rendering
5. `R:/Records/INDEX/IR-261003-H17.txt`
6. `R:/IT/desktop-move-2026.html` and profile migration package
   - If the already-retained package contains offline PST/OST or mail-cache copies, preserve only the relevant MAIL-11/14/20 threads and their original headers, MIME parts, Content-ID attachments and sidecars. Do not connect to a live mailbox or collect unrelated mailbox contents.

Return original file contents/bytes where possible. The K08 verifier normalizes the recovered phrase, computes HMAC-SHA256 with desk nonce `5F933DA6A1BD03C32DA5CBC25344F497`, keeps the first 16 bytes, then SHA-256s those 16 bytes against the acceptance commitment.

## PTW-417 closeout cross-source records

If an independently authorized local copy exists, preserve the original signed PTW-417 closeout, field sketch, and all receipt/work-order revisions (including OPEN and REMOVED entries). The current HTML is a redacted records copy; MAIL-04 gives witness walk B/D/A/C but does not provide the original sketch or signatures. A privacy-safe yes/no attestation whether the printed E initial corresponds to Emily may help test the photo-caption link; do not request or expose full personal signatures or unrelated identity data. The cosmetic-corrosion photograph and caption/sidecar are requested under K08 item 2 above; keep them as separate objects. This is a source join to test, not proof that the photo is N14 or that it supplied K08 wording.

## AX-7782 / IR-261003-H17 native transfer object (joint K04/K08 locator)

If the user already has an independently authorized local copy, include the native object from `R:/Risk/Transfers/AX-7782/Bundle06`, all eight 1 MiB chunk files, the original manifest and per-chunk hashes, omission/retry log, transfer/queue receipt, and handoff print. Preserve transfer ID, sequence, attempt, dry_run, COMMIT/ABORT state, and source path for every file. The surviving transfer audit records an 8×1 MiB COMMIT for AX-7782 / IR-261003-H17, but the supplied export has only 2-byte checkpoints; those checkpoints are not chunk contents and must not be promoted to coupon bytes. Do not access the protected R-drive or repeat public acquisition.

## After retrieval: full coverage, no silent negative

Preserve each original and its source path, container lineage, and hash. Treat `work/h17_missing_source_intake.py` as a **narrow dispatch-ACK / named-plain-text triage**, not a complete source-intake or a certification that K04/K08 are absent. Its K04 path inspects a limited set of text-log filenames and rechecks only the masked ACK payload; it does not extract the physical coupon from native print media. Its K08 path searches 1–64-word contiguous spans in files whose path contains selected keywords; unnamed images, workbooks, archive members, and other sidecars can be missed.

Run the existing complementary read-only tools on any authorized recovered tree, as suitable to its content:

1. `work/h17_k04_binary_window_intake.py` for native/coupon/print/transfer bytes, nested containers, grouped hex, and supported EMF/XPS text extracts. Preserve all original-versus-extracted byte mappings.
2. `work/h17_profile_inventory.py` followed by `work/h17_profile_k08_phrase_scan.py` for named and unnamed caption candidates, Office/images/profile caches, XPS/EMF, and archive/container variants. Respect the scanner's explicit limits and separately authorized mail inclusion.
3. `work/h17_witness_intake.py` for proposed whole-object coupon and whole-caption transcriptions attached to preserved originals, then check the unchanged official `resources/verify.py` and acceptance commitments. A hash hit does not independently authenticate original provenance.
4. `work/h17_printer_registry_allowlist.py` for an independently authorized textual `.reg` export only; it emits allowlisted HKCU printer settings and refuses binary hives. It does not parse `NTUSER.DAT`. The relevant export paths are HKCU\\Printers\\Connections and HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Devices, PrinterPorts, and Windows\\Device; do not export unrelated registry branches.

Record formats, skipped files, scan limits, extraction failures and unscanned carriers. If a path is unsupported or a bounded search has no hit, report that specific coverage limitation rather than claiming the entire recovered tree lacks the target. Do not edit acceptance commitments, verifier logic or canonical candidate to manufacture acceptance. Continue genuinely different source-indexed internal reconstruction research while retrieval is pending.

## Additional source-side join files explicitly referenced by the retained bookmarks

- R:/IT/desk-images/oldscan/scanrelease.txt (bookmark description: BX25 folios used a four-position numeric release setting; paper key register stayed with the Risk desk)
- Risk-desk paper key register (physical register; the bookmark does not provide a separate path)
- R:/Risk/Transfers/BX25/transfer-index.htm
- R:/Stores/consumables/mug-stock.xls
- R:/IT/desktop-move-2026.html
- R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx

Prioritize the first three because the surviving bookmark set directly points to the old-scan release register, BX25 transfer index, and mug-stock workbook. They are source-side joins, not replacements for the missing native coupon or final margin.

## Additional K08 native-label discriminator

PS-261003-0300 is a 07:00Z LABEL/store spool record preceding the numbered spool series; its role as an envelope label is unverified, and the five-minute ordinal proximity does not authenticate that role. If an independently authorized local copy is supplied, retain its native .SPL/.SHD/EMF/PRN or rendered output, queue/job/dispatch manifest, and any physical shelf card/label with collection receipt. Keep PS-0323 as an unverified payload candidate; the N23→PS0323 join is not source-authenticated.

## K08 shelf-card and caption carriers

MAIL-12 says the small card by the shelf contains the words and warns that its heading is only the place where it was pinned. N12 identifies the tea-stained shelf card as the relevant one, not the clean card. If an independently authorized local copy exists, preserve both the tea-stained card and clean comparison card in situ; capture front and back, heading/pin location, paper/ink, handwriting, and any associated photograph or caption sidecar. Keep heading/location metadata separate from the phrase itself. Do not assume the card was printed by PS-0300 or PS-0323 without the native queue/job/dispatch manifest.

## K08 caption sidecars

Also retrieve the pre-incident crew photograph/galley-caption archive in full, including original images and any N25–N36 caption sidecars, authorship, timestamps, revision history, thumbnail/preview cache and unsaved/AutoRecover copies. The retained N01–N24 text is not the final envelope wording.
