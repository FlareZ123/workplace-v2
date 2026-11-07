# H-17 REC8/1: precise request for missing preservation evidence

**Status:** Internal source-dependency list only. No external request has been sent. The root README states that the 21 October custodian channel is closed and must not be reopened; do not submit this file through that channel. Use these leads only if a new authorized custody path or unsolicited source delivery becomes available.

**Prepared:** 2026-10-20 UTC. **Purpose:** Finish the original eight-component recovery without fabricating bytes or modifying the verifier. This is a records request, not an equipment-action instruction.

## Already recovered
K01, K02, K03, K05, K06, K07 independently pass their original SHA-256 commitments. See [current recovery index](README.md) and [reproducible recovery report](agent3-six-validated-components.md). The official acceptance output for the six-value partial candidate is `passed=6`, `combined=INCOMPLETE`, `accepted=false`.

## Missing record A: K04 coupon payload
- **Exact logical route:** `ESC-N`, incident-date September mapping to `PS-261003-0417`.
- **Relevant printer event:** 2026-10-03 18:02 UTC, `ATTEMPT=2 STATE=ACK CLASS=RECOVER`.
- **Problem:** surviving printer reconstruction claims payload `A9A9DC5731A5E2AE879C47215C2559D5`. XOR with the supplied mask `8556C8CB6140A7F9A5123AC7571BEE1C` gives `2CFF149C50E54557228E7DE60B3EB7C9`, but the untouched K04 verifier rejects these derived bytes.
- **Source warning:** custodian note and MAIL-16 explicitly warn that dispatch ACK confirms a job, without confirming reconstructed payload byte integrity.
- **Needed:** an independently retained original coupon, verified 16-byte payload transcript, uncorrupted archival spool/source image, or authoritative printer-side checksum tied to this exact job and ACK attempt. The unencrypted vendor/property register links `L-29/N` / `FA-17` / `H17-POL-17/A3` to the separate `BX25/08` transfer reference, providing provenance only. The encrypted BX25-08 folio's contents are unknown; make no claim about whether it contains coupon bytes.

## Missing record B: K08 keeper's final caption
- **Owner of remembered wording:** Emily; personal late-watch desk/envelope caption distinguishing the keeper envelope.
- **Problem:** source N02/N06 are marked drafts and N17/N18 are explicitly older standby and commissioning envelope labels. MAIL-11, MAIL-20 and N23 distinguish a final wording that the surviving export does not reproduce.
- **Needed:** the final keeper-envelope label, photograph with legible signed caption, original desk notebook margin, or complete correspondence that records Emily's exact final wording. A thematic paraphrase of the sea, night, lamp, cups or room at the table cannot independently establish the HMAC input.
- **Available check:** the original normalization and HMAC procedure is in `resources/evidence/recovery-routing.json`; the immutable acceptance is `resources/acceptance.json`.

## Source retrieval boundaries
The supplier reconciliation independently identifies RN-052 / BX25/08 as a property-annex scan inward transfer. The encrypted BX25-08 folio remains unopened under an authorized release procedure; its contents, any linked website, and any portal are unknown. Do not use or propagate URLs, organization names, portal descriptions, or account details previously attributed to the folio. The unencrypted office bookmark separately points to the BX25 transfer-index file and records that the paper key register stayed with the Risk desk.


## Additional original-source locator
The surviving `retired-office-bookmarks.html` explicitly names `file:///R:/Records/INDEX/IR-261003-H17.txt`, an *original Windows mapped-drive incident desk index*. That source file is **not supplied** with the export. A preserved authorized copy of this exact historical file and the record paths it indexes should be requested from the records custodian. The pointer alone neither establishes the file's original date nor contains missing component bytes. The previous workspace tested four related anonymous public URLs and received 404; the Windows `R:` path is distinct from those URLs. See [predecessor source-addressed intake](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-missing-evidence-intake.md).

## Research-prior-art gate
Predecessor repository [workplace-v1](https://github.com/FlareZ123/workplace-v1/blob/main/results/README.md) contains extensive analysis of the *same original archive*, including [two independent exhaustive three-byte K04 correction sweeps](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-three-byte-bound.md) with **9,285,570,000 variants each and zero match**. A redundant v2 matrix was cancelled after this prior work was discovered. The research frontier remains additional actual K04 source bytes or verbatim K08 words. See [v2 cross-repository gate](h17-v1-prior-art-gate.md).

## Specific offline custody retrieval leads (conditional, no original recovered)

The claim that a particular network service desk or local archival station was the incident host came from an unauthenticated extraction of the encrypted BX25-08 PDF and is withdrawn. The release setting was obtained by exhaustive search, with no Risk-desk paper-register entry cited. Do not use or propagate any derived PDF content. The current local evidence does not identify a historical print host. Only the original Risk-desk paper key register or another independently authorized release record can authorize access. See the withdrawal notice and corrected source-availability gate.

An **authorized historical print-host image**, *if one exists* and independent host records identify the machine that queued PS-261003-0417, could contain original .SHD/.SPL job material or the contemporaneous spool journal at 3 October 18:02 UTC. Completed print jobs are normally removed; neither Windows, retention nor snapshot survival is established. The unencrypted bookmark to R:/IT/desktop-move-2026.html is a profile-replacement-calendar locator, not proof that the profile or print queue belonged to FA-18. Request the calendar and profile mapping, and identify the host from independent records before prioritizing a whole-system image. If an authorized workstation image is obtained, inventory it for system spooler artifacts (K04) and Bundle 06 / WN-14 / shared photo-caption directories (K08); MAIL-20 and MAIL-14 make this a cross-slot candidate, not proof those materials were stored on a particular machine. Request a historical image and queue provenance from records custody, not live equipment. See [predecessor's source-specific print-host request](https://github.com/FlareZ123/workplace-v1/blob/main/communications/agent12/20261020T0742Z_agent1-historical-print-host-spool-snapshot.md).

If independent host inventory maps a preserved retired profile to the machine that queued PS-261003-0417, preserve both the profile hive for the R: mapping and the full workstation image for possible system spooler artifacts; these are different evidence sources.

**Acquisition priority:** first recover the bookmarked R:\IT\desktop-move-2026.html calendar and the original profile-refresh/migration package, because the bookmark explicitly says the BX25 scan copies travelled with the office profile refresh. Treat the USMT store as conditional on the migration method; pursue CSC only if the historical R: mapping proves a network share and Offline Files was enabled or pinned.

**Conditional R: drive Offline Files / CSC lead (Agent34, 7 November).** The bookmarks point to several absent Windows files under R:\, including the incident desk index, scanrelease.txt, mug-stock.xls, the SEP26 return index and the profile-replacement calendar. First establish whether R: was a mapped network share. If so, and Offline Files was enabled or the relevant folders were pinned, preserve the complete configured Client-Side Cache (CSC) tree, its database/logs and the associated SYSTEM/SOFTWARE and user-profile hives from the same historical workstation image. The usual cache location is %SystemRoot%\CSC, configurable through HKLM\SYSTEM\CurrentControlSet\Services\CSC\Parameters; Offline Files policy uses Software\Policies\Microsoft\Windows\NetCache. Preserve before any synchronization, purge, reinitialization or cache rebuild. This is conditional: neither a network mapping, Offline Files enablement nor cache coverage is established. See [the detailed CSC retrieval gate](h17-r-drive-csc-offline-cache-retrieval-lead-20261107.md) and [Microsoft's CSC documentation](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/change-csc-folder-location-with-cachelocation-registry) / [Offline Files policy documentation](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-admx-offlinefiles).
**Conditional profile-refresh migration-store lead (Agent34, 7 November).** The bookmark export says the BX25 scan copies travelled with the office profile refresh. Preserve the original profile-refresh/migration package and its manifest/logs regardless of technology. If USMT was used, request the original compressed migration store, ScanState.log, LoadState.log, Progress log, ListFiles log, USMTDiag.xml, Config.xml, MigDocs.xml, MigApp.xml, MigUser.xml, all custom migration XML, source/destination host and store path. ListFiles records the files gathered; Progress/diagnostic logs can identify the source host, command line, detected users, included components, migration units and errors. USMT stores may be remote or local; do not assume the store is beside the profile image. Preserve and hash the original before verifying a working copy with UsmtUtils /verify; do not run LoadState or repeat ScanState against the source, and do not guess/bypass any store encryption. USMT may omit PST files if Outlook was open during ScanState, so absence of a PST from the store does not prove it never existed. Migration technology and file inclusion remain unproven. See [the detailed migration-store retrieval gate](h17-profile-refresh-migration-store-retrieval-lead-20261107.md) and [Microsoft's USMT guidance](https://learn.microsoft.com/en-us/windows/deployment/usmt/getting-started-with-the-user-state-migration-tool), [log-file reference](https://learn.microsoft.com/en-us/windows/deployment/usmt/usmt-log-files), and [compressed-store verification guidance](https://learn.microsoft.com/en-us/windows/deployment/usmt/verify-the-condition-of-a-compressed-migration-store).

**Both are evidence acquisition hypotheses**, yielding zero coupon bits or exact caption words until an actual independent historical file is supplied. Their utility is a precise source/selector for custodian review, distinct from speculative key bytes. No request for protected portal credentials or new live-system interaction is implied.

## Acceptance procedure
Once authentic missing evidence becomes available, derive 16-byte K04 and K08 candidates under the original route rules, check each via the **unchanged** `resources/verify.py`, and require all eight individual `PASS` results plus `combined=PASS` and `accepted=true`. Until then, report the combined recovery key as **unverified**.


## Conditional K04 earlier-source witness windows, cross-checked against original spool timestamps (Agent 4)

A separate **source-geometry-dependent** investigation in the predecessor, [constructive causal nullspace](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-p955-constructive-128bit-causal-nullspace.md), identifies three unobserved candidate generator-state intervals that could carry information about the disputed four-word coupon under a particular common-MT19937 producer and bounded chronology model. The timestamps below are the **original retained printer job timestamps bracketing the gaps**, not independently observed times of PRNG computation:

| Conditional missing-state window | Recorded job before / UTC | Recorded job after / UTC | Under the conditional reference index955 fixture |
|---|---|---|---|
| row12→13 | `PS-261003-0312`, 03 Oct 08:00 | `PS-261003-0313`, 03 Oct 08:05 | hidden predecessor `X[104]` |
| row43→44 | `PS-261003-0343`, 03 Oct 10:35 | `PS-261003-0344`, 03 Oct 10:40 | hidden state `X[332..335]` |
| row96→97 | `PS-261003-0396`, 03 Oct 15:00 | `PS-261003-0397`, 03 Oct 15:05 | hidden middle `X[728]` and neighboring words |

All six bracketing records are `ACK` events in the unmodified `evidence/print/spool-reconstruction.log`. The published predecessor proof shows how perturbations in the hidden state slots can leave the 528 intact payload words unchanged while changing every bit of the selected coupon; the spool alone cannot authenticate their historical values under that model.

**Acquisition use:** If an authorized records custodian already has an *independent, historically indexed printer-state/diagnostic export* mentioning exact producer draw indices for the original incident-day jobs, the three bracketing intervals offer specific places to check for a missing output witness. A contemporaneous original coupon for `PS-261003-0417` attempt 2 remains the preferred direct evidence, irrespective of generator models. The 5-minute windows do not imply that PRNG state was necessarily generated during that five-minute period: buffering, asynchronous scheduling and separate producers are unestablished. They are provenance search anchors only. Do not infer target bytes, reproduce unprotected printer access, or treat these conditional MT indices as real without independent validation.

These are additional *testable source locator descriptions*, not three new original observations and not a change to the six-PASS/two-MISSING acceptance result.


## Additional source locators identified 6 November 2026

### K08: WN-14 folder custody boundary

MAIL-14 is David's 2 October message, **"WN-14 signed / pencil note removed"**. It distinguishes the crossed-through pencil standby transcription from Emily's desk notes: the desk notes were **under the WN-14 folder**, outside the controlled-copy sleeve, and the photographs/galley captions were separate from the engineering procedure. Request the preserved original WN-14 folder with the material physically under it, the associated desk-note originals, photograph captions, and any margin annotations, retaining their original order and provenance. This is a more precise locator for the already-requested final caption evidence.

MAIL-03/06 identify a separate WN-14 register source set that should be preserved independently of that folder/desk-note grouping. Request the original ordinary duty sheet carrying the ink groups from beneath its clear cover in the night-folder context, and both photocopies reported in Emily's tray. MAIL-03 distinguishes this ordinary duty sheet from a separate standby sheet with a grey diagonal line; preserve that standby sheet separately, and do not assume it is the same object as David's pocket-book standby transcription ending 5E67. Preserve the clear cover, lifting top label, scanner-clipped right edge, two-column layout, A/B/C/D order, exact byte spacing/separators, fold through the second box, both faces, pencil crossings, spare printed sticker removed from the cover and loose label pile (including the prior-month drill label). Obtain the original night-folder, Emily-tray and incoming-watch custody records. Retrieve native MAIL-03/06/14 headers, MIME structure and attachments after authenticating the original mail namespace; the supplied Date headers do not establish the photocopies' creation order. This is primarily a K01 provenance retrieval. Treat it as K08-relevant only if the original sheet or copies contain an explicit cross-slot selector or book pointer; the K08 routing source remains the keeper's desk phrase, crew notes and noticeboard drafts. Do not infer page/word semantics from the bytes. See [WN-14 signed-sheet and photocopy custody locator](h17-k08-wn14-signed-sheet-custody-locator-20261107.md).

MAIL-11's primary subject is **"RC-17 issue receipt"** (Emily, 1 October). It contains an embedded paragraph describing the keeper desk phrase, but should be preserved as a mixed-purpose issue receipt, not reclassified as a dedicated K08 message. MAIL-20 (Gabriel, 4 October, **"Preservation bundle 06 / desk-caption wording"**) is the preservation-bundle message explicitly about the keeper component and its route-sheet normalization/nonce. Keep those roles and dates distinct.

### K08: tea-room stock workbook (contextual lead only)

The surviving `retired-office-bookmarks.html` contains the exact historical local bookmark `file:///R:/Stores/consumables/mug-stock.xls`, labelled **"Tea-room stock sheets"**. That workbook is not in the 46-file local export. N11, MAIL-02 and MAIL-12 independently refer to the chipped blue mugs, window and little lamp. Request the preserved original workbook, if it survives, including hidden sheets, comments, formulas, cell metadata and original file timestamps. This is a **contextual source locator**, not evidence that the workbook contains Emily's final words; do not treat any paraphrase or inferred spreadsheet content as the HMAC input.

### K08: tea-receipt date bound and prior-supply trace

According to the surviving export Date fields, MAIL-09 is 1 October 2026, 08:03 UTC and observes the tea receipt being used as a bookmark in David's map-back book in the television room; MAIL-12 is 2 October 2026, 06:33 UTC and reports a tea order arrival. The original mail-store send times are not authenticated because the export uses rewritten incident-date Message-IDs, so this ordering is provisional until native headers confirm it. If confirmed, the 2 October order is too late to be the receipt already present in the book on 1 October. Independently, the galley/stores log's 30 September boat manifest includes two boxes of tea; this is a plausible earlier supply lead, not proof that its delivery record is the bookmark.

When the book and bookmark are retrieved, preserve the receipt in situ and record both faces, date, vendor, amount, transaction/reference number, item description, and any handwritten annotation before separating it from the page. If native mail headers confirm the Date ordering, prioritize receipts or delivery records earlier than 1 October; use the missing `R:/Stores/consumables/mug-stock.xls` as a contextual cross-reference. The bookmark export also lists `R:/Finance/PrevERP/bench-expenses-2025.xls` ("Bench expense allocations 2025"); this is a conditional secondary lookup only if the receipt's date/vendor/reference makes it relevant. Keep `posted-items-26.xls` and `reversal-register.htm` scoped to the already-requested K04 ST-112 R3/A3 and R4/A4 settlement evidence unless an explicit receipt cross-reference is found. Do not infer the receipt's identity from the 30 September manifest or the 2 October tea order.

Also request the original 30 September boat manifest and its personal-mail/parcel receipt or delivery list, with recipient, parcel identifiers, and any associated docket. The surviving galley/stores log records only the generic item "personal mail" alongside the two tea boxes; if the book reached the television room through that run, the original manifest could establish its custody and possibly identify the sender or accompanying receipt. This is a retrieval hypothesis only: do not assume the book or bookmark was on that manifest.\n\nThis narrows the physical-book retrieval by time without treating the receipt as K08 wording or a page-word key.

### K04: separate monthly consumables return

The 4 October print-fleet retirement note says the rollers and feed brackets were handled on a **separate monthly consumables return**. The supplied `supplier-reconciliation-L29.csv` is the five-ticket L-29/N supplier return-set check; it is not that monthly consumables return and does not establish the physical cassette identity. Request the original monthly return covering the incident-period FA-17/North printer/cassette, its source index, and any associated cassette/lot/serial or media-retention fields. The bookmark `file:///R:/Stores/returns/SEP26/index.htm` is a historical locator to the September returns index, not proof that the relevant monthly return is present there.

The same bookmark describes the September cassette-return index as a **vendor ticket list whose binder pages were signed at the north and south cabinets**. Request the original index together with those signed pages, front and back, and any attached print strips, physical coupons, duplicate receipts, scan/copy records, serials and provenance, plus any carbonless duplicate, underlying sheet or transfer copy physically retained with the R3/A3 packet (if present). Do not conflate such a physical underlay with the separate R4/A4 held settlement duplicate. Cross-reference the **North** page to L-29/N / FA-17 / H17-POL-17/A3 and the **South** page to L-29/S / LV-42 / CS-18/5. The North page is a possible independent witness for PS-261003-0417; the South page is a possible same-role control for PS-261003-0448 only if its original provenance links the page to that job. Ask explicitly whether either page carries a complete 16-byte physical output or copy receipt. Keep this September index and its signed pages distinct from the separately requested incident-period monthly consumables return: the bookmark proves the locator and the existence of a signing practice, not the pages' contents, incident coverage or survival.

These three leads are grounded in the surviving bookmark, MAIL-14, and print-fleet note. They identify missing originals for custodian retrieval; they add **zero recovered K04 bytes and zero exact K08 words** until the originals are supplied and authenticated.


### K04: Risk transfer index and paper key register

The retired-office bookmark file also points to `file:///R:/Risk/Transfers/BX25/transfer-index.htm`, labelled **"2025 risk scan transfer index"**. The supplier reconciliation independently records `RN-052` as RISK/R1/FILED, asset `FA-17`, folio `BX25/08`, described as a property-annex scan inward transfer; `RN-053` is the LV-42/BX25/12 hired-plant certificate, and `RN-047` is the ST-09/BX25/03 stores-float exception. The bookmark description says the old capture terminal stored BX25 folios with a four-position numeric release setting and that its **paper key register stayed with the Risk desk**.

Request the original BX25 transfer index and a preserved scan/custody record of the Risk desk paper key register, especially the entry for FA-17 / BX25-08 / H17-POL-17/A3. Retain page order, annotations, issue/return entries and provenance. No authorized source establishes a release value. Do not use or propagate any previously circulated numeric setting or derived content. Preserve the original encrypted PDF unchanged; only the actual paper-register entry or another independently authorized release record can authorize access. This is a physical/source locator, not evidence that the register contains the K04 coupon or that the PDF password is a REC8 component.


### K08: electrical-group roster

The same surviving bookmark export lists `file:///R:/IT/staff-groups/EG.htm`, titled **"E.G. electrical group roster"**. Request the preserved original roster, including any embedded photographs, profile links, annotations and file metadata. It may identify the people connected with the night-watch photograph or help locate the retired profile. Its contents are unknown; it does not establish any caption words.

### K08: pre-incident shared photo-caption archive

MAIL-11 (Emily, 1 October 2026 18:14 UTC) says the desk notes and photograph captions were how she worked out the final desk phrase, two days before the 3 October incident. The relevant caption material therefore may predate the incident and may not be authored or owned by Emily. The surviving notes attribute N01/N08 (empty-bench and window/water photographs) to Jason, N09 (galley-board first-cup caption) to Zoey, and N14 (sunrise photograph) to Gabriel; N10 refers to the photograph after the last cup without identifying its photographer or caption author; predecessor analysis contextually links that reference to Jason's N01 empty-bench photograph, a cross-author candidate rather than a proven same-image/adoption link. Prioritize the N01 original image and caption as a testable locator while keeping N02/N06 as Emily-authored exact-language controls. MAIL-14 separately confirms that photographs and galley captions were kept apart from the engineering procedure. Keep MAIL-08 gland-residue/engineering photographs distinct.

Request the original shared crew/noticeboard/galley photo-caption archive, including pre-1 October images and captions, original image/negative/scan files, any physical prints (both faces, reverse-side handwriting, lab/date stamps, crop/adhesive marks and original album/board order), EXIF/IPTC/XMP metadata, sidecars, album/folder membership, caption author/editor, edit history and separate photo-creation versus caption timestamps. Do not restrict retrieval to Emily-owned images or 3 October incident photographs. A generic thematic caption is not K08: require a defensible source link from the pre-incident caption to Emily's final incident-envelope margin before applying the K08 HMAC. The note entries have no per-entry dates, and MAIL-11 does not identify a unique photograph or quote the final words.

See [K08 pre-incident shared photo-caption acquisition rule](h17-k08-preincident-photo-caption-acquisition-20261107.md). This is a source-scope discriminator, not recovered phrase text; do not reopen the closed 21 October custodian channel.


### K04: former finance posting and reversal records

The bookmark export also lists `file:///R:/Finance/PrevERP/posted-items-26.xls` and `file:///R:/Finance/PrevERP/reversal-register.htm`. These may provide an independent original record of the A3 posted versus A4 held-duplicate settlement already summarized in `supplier-reconciliation-L29.csv`. Request the original files with workbook formulas, hidden sheets, comments, reversal references and timestamps if they survive. Specifically obtain both original entries and any receipt images for **ST-112 R3 POSTED/A3** and **ST-112 R4 HELD/A4 duplicate**, the only duplicated L-29/N ticket in the supplied reconciliation. Preserve the reversal/hold record and do not infer that R3/R4 or A3/A4 correspond to spool ATTEMPT values. Their relevance to the physical coupon is unproven; they are provenance/version-selection records, not coupon bytes.



### Correction: MAIL-20 source reference

A previous draft misread the header of `evidence/mail/20.eml`. The supplied original has `X-Records-Reference: MAIL-20`, not `desk-note-04`. A direct search of the uploaded ZIP and repository finds no `desk-note-04` reference. Do not request or infer a separate record on that basis. MAIL-20 itself says the bundle is trimmed and that several captions and drafts existed on Emily's desk, but it does not identify a separate note record. The bookmark's `R:/IT/desk-images/oldscan/scanrelease.txt` remains a separate historical source locator, with no established link to a specific desk note.

### K04: hired-equipment loan-set register

The bookmark `file:///R:/Risk/hired-plant/CS-18/loan-set-register.htm` is titled **"Hired equipment certificates"** and carries a note that LV-series settlement queries were handled at the contractor desk. Request the original register only if it can identify equipment, serials or custody relevant to the incident-period printer/cassette. The connection between CS-18 and FA-17 is currently unestablished, so this is a lower-priority locator.

None of these three files is present in the uploaded ZIP, either repository's current recursive tree, or plausible resource/private paths in v1/v2 Git history. The surviving bookmark is the only located witness. These requests add no K04 bytes and no K08 exact words until an original is supplied and independently authenticated.


### K04/K08: native mail source for MAIL-16 and MAIL-20

The supplied 20-message `.eml` export is structurally incomplete for source reconstruction: all 20 messages are single-part `text/plain`, none has `In-Reply-To`, `References`, or `Thread-Index`, and none carries an attachment or additional MIME part. The mail index says repeated quoted text was omitted; the custodian note confirms that quoted reply material is omitted and the export is not the full incident record.

Request an authorized native source for **MAIL-16** (Simon, 3 Oct 2026 07:49 UTC, “Escrow print jobs / recovered buffer”) and **MAIL-20** (Gabriel, 4 Oct 2026 11:06 UTC, “Preservation bundle 06 / desk-caption wording”), plus only their directly related messages from 28 Sep to 4 Oct 2026. Acceptable forms include original RFC 822/MIME messages, a scoped mailbox export, or the relevant server journal. Preserve full original headers and thread IDs, complete bodies including quoted text, original MIME structure and attachments with hashes, UTC timestamps, and export provenance. MAIL-16 may carry original spool/coupon or receipt evidence; MAIL-20 may carry exact caption wording or related source material. The current export proves neither attachment existed nor that the omitted material contains either target. Do not request an unrestricted personal mailbox dump or infer any missing bytes/words from this locator.

See [native-mail source-gap analysis](h17-k08-native-mail-source-gap-20261106.md). This is a targeted retrieval lead, not a recovered component.


### K08: MAIL-12 shelf card and version boundary

MAIL-12 (Zoey, 2 Oct 2026 06:33 UTC) says a **small card was placed by the shelf** for the chipped blue mugs belonging to two night-crew members; the card's words are not in the export. MAIL-11 (Emily, 1 Oct) predates it and records intent without quoting the final phrase. MAIL-14 (David, 2 Oct) locates Emily's personal notes beneath WN-14, separate from controlled procedure. MAIL-20 (Gabriel, 4 Oct) says Emily selected exact words among several captions/drafts. The bookmark export separately points to the absent `R:/Stores/consumables/mug-stock.xls` workbook. This creates a plausible **literal quotation / draft-version boundary** between the 2 Oct shelf card and Emily's final selection, but no surviving record proves she saw or adopted the card.

Request the original shelf card (front/back, handwriting, date, later edits), any contemporaneous photograph/scan and native catalogue metadata, and the original `mug-stock.xls` with hidden sheets, comments, formulas, embedded objects and revision history. Include native MAIL-11, MAIL-12, MAIL-14 and MAIL-20 plus directly related messages only, preserving quoted text, full headers, MIME parts, attachments, timestamps and provenance. Do not infer card wording from MAIL-12 or N11, and do not promote it to K08 without an explicit link to Emily's final envelope inscription.

See [K08 shelf-card literal-source lead](h17-k08-shelf-card-literal-source-20261106.md) and [native-mail source-gap analysis](h17-k08-native-mail-source-gap-20261106.md). This is a new source locator, not a recovered phrase.


### K08: earlier first-person MAIL-02 antecedent

Include native MAIL-02 (Emily to Zoey, 28 Sep 2026 14:46 UTC, “Galley freezer and the soup tubs”) in the scoped source request, preserving complete headers and any original thread/quoted material. It predates N02 and records Emily's request to keep clean bowls for late arrivals who had eaten out of mugs after the dishwasher finished. This may be an antecedent to the later “making room” language, but the current body does not quote the final caption or prove that N02 descended from it. Use the native message only to establish whether any exact wording was quoted, forwarded, rewritten or dropped. The full K08 message set is now MAIL-02, MAIL-11, MAIL-12, MAIL-14 and MAIL-20, plus directly related thread records only.


### K08: preserve original desk-draft versions

In addition to the shelf card and native mail, preserve the original N02, N06 and N23 desk artifacts (paper originals or native files), including all dated versions, margin corrections, handwriting, reverse sides, comments, scan sidecars and custody notes. The surviving note extract labels N02 “first draft”, N06 “second desk draft”, and N23 says the margin wording was not the final envelope text. N06 shares “little lamp” and “corridor” anchors with MAIL-12, while N02's room/next-watch theme is consistent with MAIL-02's late-arrival/bowl context. These are source-lineage clues only; chronology and literal copying are unproven. Do not infer a final caption from them.


### K04: AX-7782 transfer-queue metadata and checkpoint selection

The supplied `evidence/transfers/queue-note.txt` says the receipt ledger can contain COMMIT entries for dry runs and explicitly directs the reader to the queue's `mode`, `purpose`, and `dry_run` fields to select the actual handoff. It identifies AX-7778 as a pre-incident drill export, AX-7781 as a dry run, AX-7783 as stopped before handoff, and AX-7782 as the actual retained copy. It also says each checkpoint is a 2-byte opaque field.

The supplied `transfer-audit.jsonl` contains eight AX-7782 chunk sequence numbers with two attempts each, but its chunk events have no `mode` or `purpose`; its COMMIT records contain only `dry_run`, chunk count, object, and receipt time. AX-7778 and AX-7782 both have `dry_run:false`, so that field alone does not select the actual transfer. The local `evidence/transfers/` directory contains only the queue note and audit ledger; the queue export itself is absent. The audit also does not identify which attempt was accepted for each chunk.

A bounded test treated one checkpoint per sequence as a 16-byte coupon/component: all 256 per-sequence attempt selections, forward/reverse sequence order, per-pair byte reversal and both coupon-mask/component roles (2,048 assignments) produced zero K04 hits. Pairwise XOR/add/sub and hybrid-byte variants (1,056 more) also produced zero. This rejects only those simple constructions; it does not establish that the checkpoint vector is related to K04. See [AX-7782 checkpoint-vector test and queue gap](h17-k04-ax7782-transfer-checkpoint-vector-test-20261106.md).

**Request:** the preserved historical transfer-queue export or queue-entry record for AX-7782 / IR-261003-H17, including original `mode`, `purpose`, and `dry_run` fields; per-sequence accepted-attempt selection; checkpoint serialization/interpretation; queue ordering; and any receipt/coupon association. Request an offline custody copy and its provenance. This is a source/selector request, not a claim that the queue contains the coupon or authorization to access a live transfer system.


## Separate source request: FA-17 / H17-POL-17 / A3 risk-renewal ledger

The supplier reconciliation assigns the L-29/N return set to account reference `FA-17/H17-POL-17/A3`. The retired-office bookmark export separately identifies the exact file locator `R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx`. This is distinct from `RN-052 / BX25/08`; the latter's property annex must not be treated as a substitute.

Request the original `renewal-ledger-2025.xlsx` workbook and complete folio A3, including its native formulas, hidden sheets, comments, embedded objects, asset schedule, annexes, attachments, transfer/scan index, revision history, and any supporting records that identify the L-29/N cassette, printer, archive appliance, or H-17 incident-preservation equipment. Specifically request any cross-reference that connects the five posted L-29/N service tickets to print job `PS-261003-0417`, and ask the custodian to state explicitly if no such cross-reference exists.

Preserve the original workbook and metadata. Do not merge this request with the separate `RN-052 / BX25/08` property-annex request, and do not infer that the FA-17 ledger contains the missing coupon. The current export establishes the account reference and bookmark locator only; the workbook itself is absent.


## Separate source request: complete L-29 route-control packets and transfer-index entries

The unencrypted print-fleet retirement note and supplier-reconciliation CSV establish three distinct return sets. The selected K04 route is `PS-261003-0417 / ESC-N / L-29/N / FA-17 / H17-POL-17/A3`, with five tabs: ST-094, ST-081, ST-106, ST-099, and ST-112 (tab 05, catch cleaning). The South control is `PS-261003-0448 / ESC-S / L-29/S / LV-42 / CS-18/5`, with five tabs including ST-142 (tab 05, catch retain; the CSV describes a catch pin). The separate Watch-Spare control is `PS-261003-0420 / WATCH-SPARE / L-29/W / ST-09 / STORES/FLT`, with ST-157 and ST-164 spare-inspection records.

The CSV's inward-transfer rows map RN-052 to FA-17/BX25/08 (property-annex scan), RN-053 to LV-42/BX25/12 (hired-plant certificate), and RN-047 to ST-09/BX25/03 (stores-float exception slip). These records provide a three-way control for distinguishing the selected North route from South and Watch-Spare. No authorized local source maps a route to FA-18; the South account is LV-42. The withdrawn PDF-derived FA-18 asset/host attribution must not be used.

Request the complete original North R3/POSTED/A3 five-tab packet, front and back, with attachments, serials, signatures, posting marks, and any underlays. Prioritize ST-112 and any item or record removed/retained during the catch-cleaning work. Preserve the separate ST-112 R4/HELD/A4 duplicate as a comparison object, not as the selected original. Request the complete South R3/POSTED/CS-18/5 five-tab packet, especially ST-142, as the catch-work control; request the L-29/W Watch-Spare ST-157/ST-164 records as a separate control. For ST-112 and ST-142, ask the custodian to state what physical part "catch" denotes and whether any coupon or printed material was recovered; do not assume either refers to an output tray.

Request the original transfer-index entries and associated source images for RN-052/BX25/08, RN-053/BX25/12, and RN-047/BX25/03, preserving original metadata and custody marks. These are distinct from the renewal ledger and from the encrypted BX25-08 PDF. The paper key register remains the only authorized route for accessing that encrypted PDF. Also request original asset-register entries and model/serial/configuration records for account references FA-17, LV-42 and ST-09, with an authoritative mapping of ESC-N, ESC-S and WATCH-SPARE to physical printers, cassette sets, queues and storage devices. Ask the custodian to distinguish account IDs from physical asset IDs and to state whether the South/Watch devices are valid hardware controls for the FA-17 device-local saved-job question; do not assume shared model or host.


## Separate source request: complete H-17 rounds notebook (pages 1–11)

The retained `maintenance/inspection-rounds.log` identifies itself as a local notebook transcription and explicitly says **page 4 of 11 retained**; the rest of the notebook is absent from this export. Request the original complete notebook, including pages 1–3 and 5–11, its cover/index, any inserts or attachments, page-order record, and any scans or transcription/UTC-conversion notes.

Prioritize the entries surrounding 3 October 2026 17:12–21:15 UTC and any references to the archive appliance, printer/cassette, recovery card, electrical odor, fire response, or preservation actions. Ask the custodian to confirm whether the missing pages survive and, if not, whether they were separately scanned or transferred.

Keep this notebook request separate from Emily's personal notebook-margin request for K08. The retained page establishes that six other pages are missing; it does not establish that they contain either missing component. Their value is as potential independent incident timing and equipment-state evidence for the K04 source-selection question.


### AX-7782 retained object payload (in addition to queue metadata)

MAIL-13 and the queue note identify AX-7782 as the successful retained handoff for `IR-261003-H17`. The audit records eight chunk sequences, each reporting 1,048,576 bytes, with two attempts per sequence. The supplied export contains the audit/checkpoint metadata but no chunk payloads.

Request an offline custody copy of the **actual retained AX-7782 object**, including all eight original chunk payloads for the accepted attempts, the reassembled object if available, its manifest and per-chunk hashes, original sequence/order, retry/accepted-attempt selection, receipt, and chain-of-custody metadata. Preserve raw bytes and any media image or export package without recompression or normalization. If the payloads no longer survive, request the retention/deletion record and identify any other preserved copy.

This is a request for the retained data object itself, not only the queue-entry export or 2-byte checkpoint fields. The object may contain source records needed for K04/K08; its contents are not established by the current audit. Offline records custody only; no live transfer-system access.


## Separate source request: oldscan release note and desk-image archive

The retired-office bookmark export preserves the exact historical locator `file:///R:/IT/desk-images/oldscan/scanrelease.txt`, titled **Old scan release note**. Request the original `scanrelease.txt`, its parent-folder index/manifest, every image or scan it references, contact sheets, sidecars, scan settings, timestamps, revision history, and custody/transfer metadata.

This is a separate desk-image locator. The current export establishes the bookmark only; it does **not** establish that the release note contains Emily's margin, a particular photograph, or any K08 wording. Keep it separate from the WN-14 folder, the FA-17 risk ledger, and the RN-052 / BX25/08 property transfer index. Request an offline copy from records custody; do not infer or reuse any PDF release code.


## Separate source request: Bundle 06 manifest and trim/omission record

`START_HERE.md` describes the supplied preservation set as trimmed, and MAIL-20 says **Bundle 06** was staged as a local directory and reduced to the material that could be extracted. Request the original Bundle 06 directory manifest and the associated trim/extraction log: original relative paths, filenames, sizes, hashes, timestamps, omitted-file list, extraction failures, redaction/omission reasons, and any attachment or scan sidecars excluded from this 46-file export.

If the original directory survives, request a read-only custody copy or a complete metadata-preserving file listing. If it does not, request the export operator's manifest and omission/deletion record. This is a scoped request for the provenance and missing-file inventory of Bundle 06, **not** an unrestricted mailbox dump or a live facility connection. It may identify the missing source objects for K04/K08; no omitted file or content is presumed to exist.


## Separate source request: complete RC-17 records-service package

Each of the 12 retained `RC-17-scans.txt` extracts explicitly states that its **supporting process instructions and signatures are omitted**. The pages describe a records-service sequence and a required witness entry; they are expressly marked as not being plant operating instructions. Request the original controlled-copy package for the issued **revision C**, including its supporting records-service instructions, cover/index, witness entries and signatures, attachments, revision/issue history, and any preservation-reference crosswalk.

Ask specifically for any witness or preservation entry that names the recovery envelope, ESC-N coupon/print job, AX-7782 transfer, or keeper's desk phrase. Keep this request distinct from the four revision-C footer control strips already used for K07. The current extracts establish that supporting material was omitted; they do not establish that it contains K04/K08 evidence.


## Separate source request: complete H17/HST-4 historian export

`telemetry/export-readme.txt` identifies `trip-recorder.raw` as a **retained sample only**, with rows in retrieval order rather than chronological order. Request the complete native H17/HST-4 historian export for the incident period, including the channel/tag dictionary, schema and units, acquisition interval, original sequence numbers, clock-quality metadata, dropped/omitted-row map, and any power/UPS, archive-appliance, records-room, printer, or incident-alarm channels if they exist.

Preserve the native records and timestamps without sorting or normalization. Ask the custodian to state explicitly which equipment channels were never connected to HST-4. This is a supporting K04 source request: the retained sample establishes a partial event record, but does not establish that the historian monitored the printer or contains a reset/power event.


**Attempt-level spool request:** The records-custodian note says drafts and requested-but-unacknowledged print jobs survive, and MAIL-16 identifies a later requested-but-unacknowledged entry for `PS-261003-0417`. Request the native queue records and raw `.SPL`/`.SHD` material for **all three attempts** of this exact job, including the attempt-3 requested payload/draft if retained, its status transitions, spooler journal, job/driver metadata, copy/raster data, and retention/deletion history. Treat attempt 3 only as a comparator/control: MAIL-16 says it had no acknowledgement and identifies the last acknowledged attempt as the physical-print selector. Do not promote attempt 3 to the selected coupon.


## Separate source request: PTW-417 field sketch and closeout correspondence

`MAIL-04` (29 Sep 2026, Simon to Emily and David) is already present and states that the witness walk was B, D, A, C, with the sketch made looking back from the access hatch. `work-order-417.html` independently says the **field sketch supersedes cabinet lettering** and directs the reader to closeout correspondence. Request the original PTW-417 field sketch (all sides, annotations, revisions and orientation marks) and the signed closeout record/attachments referred to by MAIL-04 and the work-order, rather than another copy of MAIL-04.

Ask whether either original record independently cross-references `PS-261003-0417`, ESC-N, the L-29/N cassette, or the archive appliance. This is a provenance check of the shared **417** reference and a possible cross-record link; it does not assume the permit and printer job are related, and it does not reopen the already accepted K03 serial component or its ordering.

**Resolved for K03; retain the older revision-1 ambiguity only as audit history.** The K03 rule selects the highest signed revision of CLOSED AS_LEFT records per bay. Revision 2 supplies a complete signed set for A/B/C/D, so the revision-1 bay-A alternatives (SG-7E73B4CC and SG-574A9232) do not affect K03. In MAIL-04's B,D,A,C witness order, the selected revision-2 serials are SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD; joining exactly as printed with | and taking SHA-256(ASCII)[:16] yields accepted K03 1384AF96E25D6ADA666209CB55E062FA. Do not request another K03 receipt to resolve the superseded revision-1 A row, and do not reuse either revision-1 A serial as a K04 input. The original field sketch/closeout may remain useful for unrelated physical provenance, but it is not needed to establish K03.



Also request the original signed PTW-417 work-order or a custodian-certified, privacy-safe signatory/witness crosswalk for the printed initials **S / E**. The current HTML is a records copy and says personal signatures are redacted. Ask whether **E** is the same Emily identified in MAIL-11/MAIL-20, without assuming that identity from an initial. This may establish or falsify a cross-record witness link; it is not itself evidence of the final K08 wording.


The work-order also lists a **cosmetic-corrosion photograph** as requested/outstanding. Ask whether it was taken and, if so, request the original image, caption, metadata/sidecar, and any receipt or link to the field sketch/closeout. Keep it distinct from Emily's desk/galley photographs; the current sources do not establish that this is the K08 photograph or that its caption supplied the final phrase.


**Scoped native-mail addition:** Include the original native `MAIL-04` (Simon to Emily and David, 29 Sep 2026) and only its directly related thread/attachments. It is the retained closeout email that states the B/D/A/C witness walk and is referred to by the PTW-417 work-order; the current text-only export carries no attachment or native thread metadata. Preserve original headers, quoted replies, MIME parts, attachments and any field-sketch/photo link. This is a specific closeout-thread request, not a mailbox-wide search.


## K08: television-room map-back book and tea-receipt bookmark

MAIL-09 (Jason to Zoey, 1 October 2026, 08:03 UTC) records that the library books were in the television room, that the book with a map in the back belonged to David, and that a tea receipt was being used as a bookmark and was deliberately left in place. N23 separately attributes a margin wording to Emily, but does not identify the medium, page, or book. The chronology and shared “margin/bookmark” vocabulary do not prove that Emily wrote in David's book or that the receipt carries her words.

If the physical items survive, request the exact David-owned book and bookmark **together and in situ**. Before moving anything, photograph the cover, spine, title/imprint page, edition/printing statement, copyright page and rear map; record whether the map is bound-in, folded or loose. Photograph the receipt in its original position with the marked spread, then preserve high-resolution images of both sides, folds, marks and any date/merchant/amount or recipe text. Capture the marked page and adjacent pages in full, including page numbers, section headings, complete margins, handwriting, erasures and annotations. Record custody and movement history. Keep “receipt” open to the physical item's actual form; do not infer whether it is a purchase slip or an older recipe/receipt card before inspection.

**Edition caution:** Agent23's *The Way That I Went* is a candidate, not an identified book. A 1939 second edition, revised, is also catalogued as 394 pages with a folded map of Ireland at the rear ([Ulysses Rare Books listing](https://www.rarebooks.ie/books/history/the-way-that-i-went-second-edition-1939/)). Therefore the rear-map clue alone does not identify the 1937 first edition. The physical title/imprint/edition statement is decisive. The apparent alignment of L-29/N ticket numbers 81/94/99/106/112 with *The Volcanic North*, and L-29/S ticket numbers 121/130/135/142/151 with *The Silurian Region*, remains a hypothesis; do not treat ticket IDs as page numbers without an independent original record or a verified page-level mark.

The *Riddle of the Sands* was tested only as a candidate because its public edition contains maps and maritime/night-time motifs. Its pinned printed text yielded zero K08 matches in 55,941 frozen 3–64-word motif-gated windows. MAIL-09 does not name that title. Do not treat it as the identified book or launch another literary-text sweep. The physical book, marked page and receipt are the relevant evidence; no exact K08 words are established by the current export.


### Additional K08 physical identity discriminator: David's pocket book

MAIL-06 (David, 30 September 2026) says an old WN-14 standby transcription is in “my pocket book”; its group D ends `5E67`. MAIL-09 (Jason, 1 October 2026) describes a David-owned map-back book in the television room with a tea receipt left in place as a bookmark. Same owner and close chronology make it worth checking whether these are the same item, but the export never says so. If retrieved, check whether the same WN-14 standby transcription is physically co-located. Such co-location would be new evidence that the pocket book and map-back book are the same object, but MAIL-06 does not claim this; `5E67` is not an intended identity marker, K08 value or page/word selector.

There is a stronger contextual clue in *The Riddle of the Sands*, Chapter XX, “The Little Drab Book”. The novel first lists Cowper's *Sailing Tours* among several books in Davies's library, then introduces a separate “particular volume”: an old, cheap-cloth guide for yachtsmen to a British estuary, with a title-page attribution to “Lieut. X--, R.N.”, Dollmann's name on the back, and a yacht-owner frontispiece. This narrative sequence distinguishes the guide from Cowper's book. It supports a yachtsman's estuary-guide profile, but does not identify David's physical copy or prove that the in-story guide is a particular later real-world title. The novel does not explicitly say that this guide has a map in the back. The cabin-table/sea/end-of-night scene also echoes N20, but this is a literary clue, not a recovered K08 phrase.

The printed text of Chapter XX was tested across all 242,141 contiguous 3–64-word windows with no motif gate; no K08 match was found. The whole-book motif-gated test also found no match in 55,941 windows. If this connection is real, the relevant words are more likely in Emily's handwritten marginalia or on the bookmark than in the printed chapter. When retrieving the physical book, check the Chapter-XX features above, the possible WN-14 `5E67` transcription, the marked page, adjacent pages, all marginalia, and both sides of the receipt. Keep the title and identity as unresolved until the item is inspected.


### Alternative K08 page/section crosswalk candidate: Praeger's *The Way That I Went*

Praeger's *The Way That I Went: An Irishman in Ireland* remains an alternative page/section crosswalk candidate, not the leading “Little Drab Book” candidate. It is a natural-history travelogue, whereas the Riddle clue describes a separate yachtsman's guide to a British estuary. The 1947 third edition (416 pages, rear-map-bearing) has *The Volcanic North* beginning p.62 and *The Silurian Region* p.118. The L-29/N ticket suffixes (81, 94, 99, 106, 112) all fall in the former; the L-29/S suffixes (121, 130, 135, 142, 151) all fall in the latter. In the 1997 reprint the boundary is p.111, moving p.112 to the South section. This is a page/section coincidence worth preserving, but the supplied records do not say ticket suffixes are page numbers, and the Riddle clue weakens Praeger's physical-profile fit.

If David's book survives, record its title, edition, publisher/year, pagination and rear folding map before testing this alternative. Check whether the receipt marks p.112 and whether the book or a loose insert contains the WN-14 standby transcription with group D ending 5E67 (MAIL-06). If present, record 5E67 as a physical co-location observation only; it is not a source-defined identity fingerprint or map coordinate. Available rear-map evidence describes “Ireland / Sixty Historical Divisions”. The 1937 first edition is 394 pages with a rear folding map; the 1939 second revised edition pagination remains unresolved. The 1947 third edition is the strongest checked Praeger crosswalk, not a proven unique identification. The CSV preamble defines R3/R4 as vendor settlement batches, so the ST-112 duplicate is not an edition marker.

### Alternative K08 literary/ticket-volume crosswalk candidate: Cowper's *Sailing Tours*



The Cowper set is explicitly named among Davies's books in *The Riddle of the Sands*, but the novel then describes a separate Little Drab Book; do not conflate them. The proposed North→Part I / South→Part II ticket assignment is non-discriminating: every suffix 81–151 fits within both Part I, *The Coasts of Essex and Suffolk* (1892, 168 pages), and Part II, *The Nore to the Scilly Isles* (1893, 365 pages). No source assigns either lane to a Cowper volume. Cowper remains a Riddle-named literary/physical candidate, but the page counts do not establish a ticket-volume crosswalk or identify MAIL-09's book.



If the set is found, photograph both volumes' title/imprint pages, printed pagination, map/chart placement, receipt page and all marks. Part I is listed with a frontispiece map whose reverse carries a previous-owner name; record the actual name without assuming it is Dollmann. Part II is listed with 26 charts; document their placement and any map at the back. A separate physical-profile candidate for the novel's Little Drab Book is W. Eric Wilson's 1934 *Pilot's Guide to the Thames Estuary and the Norfolk Broads for Yachtsmen* (411 pages, frontispiece and 18 folding charts); no ticket-page crosswalk is established for Wilson.



These are alternative evidence paths, not grounds for text extraction. Preserve any actual David-owned volume and receipt in situ, record the exact volume and bookmark page, and keep MAIL-14's original Emily desk notes primary.

This is a lower-priority alternative, not the custodian's primary book request. MAIL-14's placement of Emily's original desk notes under the WN-14 folder remains the primary direct K08 margin-source request.

### Leading real-world analogue for the K08 guidebook clue: Wilson's yachtsman's guide

W. Eric Wilson's *The Pilot's Guide to the Thames Estuary and the Norfolk Broads for Yachtsmen* (Imray, 1934) is the strongest real-world guidebook analogue identified so far. Bibliographic listings describe a clothbound 411-page first edition with a frontispiece, 18 folding charts and 20 photo illustrations; a 1938 second edition is listed at 404 pages. Its title and subject fit the Riddle passage's separate old guide for yachtsmen to a British estuary more closely than Praeger's natural-history travelogue. The 1934 date postdates the 1903 novel by 31 years, so Wilson is an analogue, not the fictional book's literal identity or proof of David's exact copy. No local source names Wilson's title.

The low-confidence 5E67 page/word hypothesis is 0x5E=94 / 0x67=103. Its only current page/section rationale is tied to the Praeger 1947 crosswalk and ST-094 in L-29/N; the source does not define this byte-splitting rule. Do not transfer the Praeger page/word hypothesis to Wilson without independent evidence. If David's exact Wilson copy is recovered, record the title/imprint first, then inspect p.94 as a separate falsifiable check, along with the frontispiece, every chart, rear map and verso, all marginalia, receipt bookmark and WN-14 transcription ending 5E67. The title-page attribution in listings is W. Eric Wilson D.S.O.; it does not establish the novel's fictional “Lieut. X--, R.N.” attribution.

The exact David-owned copy remains unknown. Request that guide as the leading physical-profile candidate, while keeping Emily's WN-14 desk notes, original envelope and separate photo/galley captions as the primary literal K08 sources.

### Secondary exploratory page-word experiment: Cowper's *Sailing Tours*, Parts I and II

Cowper's *Sailing Tours* is a separate book mentioned among Davies's library books in *The Riddle of the Sands*; the novel then describes a different “particular volume” as the Little Drab Book. Cowper should therefore not be treated as the leading map-back guide. Preserve the page-word experiment as secondary research only. The proposed first-edition page sets are Part I (1892): 81/94/99/106/112, and Part II (1893): 121/130/135/142/151, with word position 103. HathiTrust record 100485750/OCLC 7504145 identifies the public-domain/full-view volumes, but automated Part I page retrieval was blocked.

Agent24's actual Part II page images yield the five-word secondary fragment “solent yards sailing the even” in frozen binder-tab order [130, 151, 121, 135, 142]. The final token “even” was visually confirmed as a complete printed word on p.142 (“or even nearer”). This is not a complete K08 phrase and has not passed the K08 HMAC. No Part I word set was recovered. Preserve the images, OCR and extraction; do not continue remote Cowper alias retrieval or request Cowper as the primary map-back book. If Cowper is physically found, record it as a separate volume, not as the Little Drab Book.

See [Cowper scan-access status](h17-k08-cowper-scan-access-status-20261107.md), [volume crosswalk](h17-k08-cowper-sailing-tours-volume-crosswalk-20261107.md), [frozen locator](h17-k08-wN14-5e67-page-word-locator-20261107.md), and [Part II extraction](h17-k08-cowper-part2-word103-extraction-20261107.md).

For the Praeger candidate specifically, test whether the receipt marks p.112 and whether p.94 / word 103 (if the 5E67 split is meaningful) yields a source-relevant word. The 1947 section crosswalk places both pages in *The Volcanic North*; the 1997 reprint moves p.112 to *The Silurian Region*. This remains a low-confidence page/word hypothesis, not a decoded phrase.


### Tea-receipt bookmark cross-check

MAIL-09 says the tea receipt was deliberately left in the David-owned map-back book as a bookmark. The retired-office bookmarks also point to `R:/Stores/consumables/mug-stock.xls` (“Tea-room stock sheets”), which is absent from the ZIP. Request the original binary workbook as-is, not a CSV/PDF conversion, and preserve its original bytes/hash, file properties, hidden/very-hidden sheets, hidden rows/columns, formulas and cached values, named ranges, comments/notes, embedded objects/images, hyperlinks/external links, macros/VBA, print areas/page setup and calculation settings; include version/revision history if retained. Make a forensic copy before opening or resaving it. Request the original receipt in situ or a source-backed duplicate/transaction trace. Preserve the receipt in place first; record both sides, folds, date, merchant, amount, and handwritten marks before attempting a join. Use the former-system `posted-items-26.xls` or `reversal-register.htm` only if the receipt's own identifiers make those records relevant. Do not assume the unrelated RN-047 stores-float exception is this receipt.


## K08: conditional underleaf indentation examination

MAIL-14 locates Emily's loose desk notes under the WN-14 folder, outside the controlled-copy sleeve; N23 places the finally chosen wording in Emily's margin. If she wrote that margin while another sheet, pad leaf, folder insert or backing sheet was underneath, the lower paper may retain latent writing-pressure indentations even if the visible margin or photograph is missing. The surviving export does not establish that an underlay was present at the time of writing or that any impression survives.

If an authorized original-paper set becomes available, preserve the WN-14 folder, loose notes, adjacent pad leaves, folder backing/inserts and envelope backing sheets **in their original order and orientation**. Photograph every surface and both faces before movement or specialist processing. Do not rub, shade, pencil over, flatten, clean or chemically process the papers. Refer the originals to a qualified forensic document examiner for assessment under the applicable document-indentation standard; the examiner should decide whether optical side-lighting and/or EDD/ESDA is appropriate. EDD can affect pencil marks, so documentation must precede any such examination. Preserve raw images, settings, any lifts, hashes and an independent verbatim transcription.

A positive K08 result requires a legible inscription independently attributed by physical context and chronology to Emily's **final incident-envelope margin**. An impression of N02/N06 draft wording, N17/N18 decoy labels or unrelated notes is not K08. Apply the unchanged K08 normalization/HMAC only after source attribution. A negative examination applies only to the specific sheets examined. This is a conditional acquisition modality, not evidence that an underlay existed or that any exact words have been recovered. See [K08 underleaf-indentation acquisition path](h17-k08-underleaf-indentation-acquisition-20261107.md) and the [NIST/OSAC ANSI/ASB 044-19 standard record](https://www.nist.gov/osac/standards-library/ansiasb-standard-044-19).



### K08 physical-paper examiner sequence

The K08 underleaf route is now specified against the published document-indentation standard. On receipt of an authorized original-paper set, keep the envelope, N23 page, WN-14 folder, loose notes, adjacent pad leaves, folder inserts/backing and any directly associated shelf card in their original order and orientation. Record both faces, folds, fasteners, contact surfaces and custody before any movement. Do not remove staples, separate pages, flatten, rub, shade, clean or chemically process originals without authorization and examiner assessment.

A qualified forensic document examiner should assess suitability and first examine both sides optically under multiple lighting angles, with magnification and high-resolution imaging/video as appropriate. Under ANSI/ASB 044-19, the examiner should avoid changing impressions, obtain permission before permanent changes, determine whether EDD/ESDA is suitable, and preserve any control, lift, images and limitations. The Ohio BCI 2025 manual warns that ESDA charge can lift pencil particles and reduce contrast; photograph/copy pencil-written documents before processing. It also notes that some latent-print/DNA solvents can inhibit ESDA, so coordinate the examination sequence with the relevant specialists before treatment. Follow the receiving laboratory's validated procedure rather than attempting ESDA locally.

A negative finding is limited to the specific sheets and methods examined. Paper thickness, storage, pressure and intervening layers affect recovery; no detected impression does not prove the papers were never in contact. See [the expanded underleaf examination plan](h17-k08-underleaf-indentation-acquisition-20261107.md).

## 7 November 2026: request both competing ST↔PTW↔PS index mappings

A later source-derived audit identifies two plausible numeric offsets between the five posted FA-17 L-29/N service tickets and the same-suffix PTW/PS records. **Neither is an authenticated crosswalk.** The +304 mapping has stronger controls in the surviving export (four matched North tickets land in bays A/B/C/D in binder order, and the earlier FA-17 L-28/N holdout matches 2/2 rather than 1/2 for +300), but the original September index or a paired original ticket is still required. Do not retrieve only the +300 set, and do not promote +304 to fact.

| Ticket / source group | +300 candidate PTW / zero-offset PS | +304 candidate PTW / zero-offset PS |
|---|---|---|
| L-29/N ST-094 | PTW-394 / PS-261003-0394 | PTW-398 / PS-261003-0398 |
| L-29/N ST-081 | PTW-381 / PS-261003-0381 | PTW-385 / PS-261003-0385 |
| L-29/N ST-106 | PTW-406 / PS-261003-0406 | PTW-410 / PS-261003-0410 |
| L-29/N ST-099 | PTW-399 / PS-261003-0399 | PTW-403 / PS-261003-0403 |
| L-29/N ST-112 (R3/A3 posted; R4/A4 held duplicate) | PTW-412 / PS-261003-0412 | PTW-416 / PS-261003-0416 |
| L-28/N holdout ST-098 | PTW-398 / PS-261003-0398 | PTW-402 / PS-261003-0402 |
| L-28/N holdout ST-087 | PTW-387 / PS-261003-0387 | PTW-391 / PS-261003-0391 |

The candidate ticket neighbours for the spool gaps and selected job also differ:

| Printer record / gap | +300 candidate ST ticket | +304 candidate ST ticket |
|---|---|---|
| PS-261003-0343 | ST-043 | ST-039 |
| PS-261003-0344 | ST-044 | ST-040 |
| PS-261003-0396 | ST-096 | ST-092 |
| PS-261003-0417 (selected attempt 2) | ST-117 | ST-113 |

**Specific records to request together if an authorized new custody path or unsolicited delivery becomes available:**

1. The original R:/Stores/returns/SEP26/index.htm and its native metadata, vendor ticket list, index history, and any source/backup copies.
2. The signed North and South cabinet binder pages, front and back, including all attachments, print strips, carbonless duplicates, underlays, corrections, voids and receipt images for both candidate PTW/PS sets above.
3. The original North L-29/N ST-094, ST-081, ST-106, ST-099 and ST-112 work orders, including the full ST-112 R3/A3 posted packet and separate R4/A4 held duplicate; do not assume the numeric offset identifies the correct version.
4. The original South L-28/N ST-098 and ST-087 work orders as holdout controls.
5. The corresponding original PTW records and attempt-specific native print-job objects for both candidate sets, especially PTW/PS-412 versus PTW/PS-416 for ST-112, and PS-0417 attempt 2 itself.
6. Any contemporaneous source that explicitly pairs a service-ticket ID with a permit/job ID, including the September vendor index, signed cabinet pages, posting/reversal register or transfer/return manifest.
7. The original ST-092 and ST-096 packets together, including serial slips and attachments. Under +304, ST-092 maps to PTW-396; under +300, ST-096 maps to PTW-396. The retained PTW-396 receipt is bay C, revision 1, serial `SG-9929E382`, closed/AS_LEFT/signed. Check which original ticket, if either, explicitly cites that permit/serial. This is the most direct local-record discriminator for the gap-96 offset; the retained receipt alone does not choose a ticket.

The +304 audit's four North matches, four distinct bays, binder-order alignment, and 2/2 L-28/N FA-17 holdout are evidence for prioritizing that first-stage PTW candidate during retrieval. They are still a pattern inferred from the supplied records. The +300 candidate remains listed because it is a live competing explanation and the original index is absent. The shared cassette, asset and folio links establish a cohort/provenance association, not an individual ticket-to-job pair. See the reproducible offset audit (h17-k04-st-ptw-ps-offset-ambiguity-20261107.md) and the current source synthesis (results/README.md).
## 7 November 2026: lane-specific second-stage PTW→PS locator hypothesis

A separate, potentially compatible mapping now extends the candidate ST→PTW first stage. The two print-fleet tab-05 anchors yield PTW→PS `+1` on FA-17/ESC-N and `+2` on LV-42/ESC-S, giving composite ST→PS `+305/+306`. This is not the same hypothesis as assuming the PTW suffix equals the PS suffix in the preceding table.

Independent checks in the retained spool export:

- FA-17 L-28/N holdouts ST-087→PS-0392 and ST-098→PS-0403 are both ACK/RECOVER rows.
- South L-29/S ST-121→PS-0427 is a non-anchor ACK/RECOVER/desk row, matching the ST-142→PS-0448 tab-05 anchor's ACK/RECOVER/desk role.
- The three other predicted South jobs, PS-0436, PS-0441 and PS-0457, are outside the retained normal spool range; their absence is not a negative.
- North L-29/N ST-112 maps to PS-0417, where the selected event remains attempt 2 / RECOVER / ACK. The other four North predictions are PS-0386, PS-0399, PS-0404 and PS-0411.

The two tab-05 pairs used to derive the offsets are anchors, not independent validation. The L-28/N and ST-121 rows are holdouts, but no supplied source explicitly binds these tickets to the predicted PS jobs. A six-control PTW-serial producer screen found no simple CPython/HMAC/BLAKE2 payload matches; this does not falsify the locator. Treat the two-stage join as a promising retrieval hypothesis only. See [the full lane-specific ticket-to-spool screen and SFT](h17-k04-lane-specific-ticket-to-spool-offset-screen-20261107.md).

**Additional records to request if an authorized path or unsolicited delivery becomes available:**

1. The native SEP26 index and source schema/history, explicitly asking whether it defines a two-stage ST→PTW and PTW→PS relation or lane-specific offsets.
2. Original PTW receipts and linked source tickets for predicted PTW-385 and South PTW-425/434/439/446/455, including bay, serial, revision, signer, ticket reference and any PS/job reference. The retained PTW export covers only PTW-390..416, so it cannot test North ST-081→PTW-385 or any South `+304` first-stage prediction.
3. Complete native spool/queue records and rendered physical outputs for the South holdouts PS-0427, PS-0436, PS-0441, PS-0448 and PS-0457; PS-0436/0441/0457 are the decisive missing predictions.
4. Complete native spool/queue records for the FA-17 holdouts PS-0392 and PS-0403, and the North predicted jobs PS-0386, PS-0399, PS-0404, PS-0411 and PS-0417. Preserve the original source document path/hash and source page/range, submitting user, print processor, queue, host/device/port/route, every attempt, selector, class, destination/output tray, .SPL/.SHD or native equivalent, rendering, ACK, media-eject/collection receipt and deletion/retention history. The source-document/page fields are the direct discriminator for the proposed shared ticket/page/job index.
5. The original ST-087/ST-098 L-28/N packets and ST-121/ST-130/ST-135/ST-142/ST-151 South packets, with signed pages, attachments, carbonless copies, serial slips and explicit PTW/PS references.

Keep PS-0416 as a separate adjacent same-role blind control. Do not use the lane-specific locator to change the K04 selected attempt, infer coupon bytes, or collapse the PTW, spool-job and physical-coupon carriers.



## HST-4 historian sequence continuation and sample-to-job index

The supplied HST-4 freeze sample is explicitly incomplete and says acquisition was interrupted at 21:14. It contains 145 JSONL records: 112 PV records with sequence numbers 100–211, plus 33 DIAG_WORD records (raw_u16) across sequence numbers 0–7 and multiple revisions. No record in the supplied sample has sequence 212–227.

A candidate range-level offset aligns the contiguous retained PV sequence interval 100–211 with the contiguous spool-job suffix interval 300–411 under job suffix = PV seq + 200. The 112/112 count is not 112 independent paired observations; it follows from aligning two contiguous ranges of equal length. Treat +200 as a retrieval locator/hypothesis only. If it continues, missing seq 212–227 would map to jobs 0412–0427, including **seq 217 ↔ PS-0417**, but no per-record source crosswalk or shared generator is established. Simple fixed-gap PV-to-random mappings have already failed printer-only parity.

If an authorized new custody path or unsolicited delivery becomes available, request the **complete native HST-4/HST-4 historian export**, specifically preserving:

1. Every record for seq 212–227, with seq 217 prioritized but the whole interval retained as a holdout-capable block.
2. The original definition of the seq field and the source-authenticated sample-to-job cross-reference, including the rule that produced the observed 100–211 / PS-0300–0411 alignment.
3. Original acquisition order, timestamps with their recorded UTC offsets, tag, field, unit, quality, state, revision, and any freeze/interleave metadata. Do not deduplicate revisions or discard SUSPECT/RUN/HOLD rows.
4. All PV and DIAG_WORD records, including raw_u16 values and their revision/quality semantics, plus the native export header, interruption/restart log, and any adjacent records before/after the 21:14 interruption.
5. The source system's audit trail identifying who exported the sample, the query/time window, and whether the missing seq range was excluded, never acquired, or lost during preservation.

The existing crosswalk report is h17-hst4-pv-spool-job-crosswalk-20261107.md. The +200 range-level offset is a useful retrieval locator, not an authenticated per-record mapping; only the original HST-4 index, commissioning selector, or a paired native record can authenticate it.


## H17-POL-17/A3 office asset card and September equipment count

The surviving print-fleet retirement register provides a separate, direct source lead for the selected job: PS-261003-0417 → ESC-N → L-29/N → FA-17 → H17-POL-17/A3. It says the cassette/property references were carried forward from the September equipment count and taken from office asset cards. Neither the September 2026 equipment-count sheet nor the office asset-card set is in the supplied export or current resources tree.

If an authorized new custody path or unsolicited delivery becomes available, request:

1. The original **H17-POL-17/A3 office asset card**, both sides, including sleeve/folio, annotations, endorsements, attached slips, custody marks and any card-image metadata.
2. Adjacent **A2/A4 asset cards and revision-control records**, retaining both A3 and A4 because the North ST-112 supplier record contains an A3 posted revision and a separate A4 held duplicate.
3. The **September 2026 equipment-count sheet** covering ESC-N, ESC-S and WATCH-SPARE, with all cassette/asset identifiers, card references, location/holder fields, reconciliation marks and sign-offs.
4. The office asset-card index, card-issue/return register, and any record explaining where A3 was filed and who reconciled it.
5. Any original custody/transfer record or attached coupon/escrow reference associated with the A3 card or the L-29/N cassette.

Do not substitute the bookmarked H17-POL-17 renewal ledger for the office asset card unless an original index proves they are the same record. The A3 card and September count are a source-defined bridge from the selected PS-0417 route to a physical property record; they may validate the asset/cassette chain or identify a coupon custody location. No coupon content or serial equivalence is inferred from the surviving register. See h17-k04-office-asset-card-source-lead-20261107.md.

## 7 November 2026: additional primary-source requests and temporal gates (Agent 6)

These requests refine existing broad requests; they do not establish the proposed joins.

1. **Original supplier commissioning note.** The custodian says the supplied `recovery-routing.json` is a transcription of the supplier's commissioning reduction rules. Obtain the exact original note/version used for transcription, all pages, attachments, worked examples, marginalia, revision and distribution records. Compare line-by-line for K04 attempt/copy-stage semantics and K08 envelope/normalization/version selection. If the original is complete and identical to the JSON, close this path.

2. **Old supplier drawing named in the MAIL-16 excerpt.** Obtain the original drawing, all sheets/revisions/legend/part lists, title block, issue date, supplier, model/serial identifiers and custody. The supplied MAIL-16 excerpt says ESC-S also appears on it, while the September label transcription is current and the August service mapping must not replace it. The exported mail namespace is not authenticated; verify the drawing reference independently through the September return index, H17-POL-17 ledger, original supplier records or authenticated native source. Obtain the September current transcription and August mapping separately as version controls. Do not infer the physical meaning of “catch” before the drawing identifies the part.

The unencrypted retired-office bookmarks also include a **“Cassette service reference”** bookmark in the same Stores group. Request the original retired-office browser profile or its authorized forensic export, preserving the bookmark record, browser history, cache entries, offline/saved pages, downloads, redirects, timestamps, and associated page resources/attachments for that reference. The displayed host uses a reserved example-domain form, so do not attempt network resolution or substitute a public service page; the value of this request is any locally retained copy and its provenance. Cross-check any recovered drawing or service page against the original supplier drawing and September return index before using it. The same unencrypted bookmark export says BX25 scan copies travelled with the office profile refresh. Also request the original retiring-office profile backup/image and migration package identified by the desktop-move-2026 calendar, including the migration manifest, local file-cache copies, downloaded/saved files, recent-file/path records, timestamps and source/destination profile mapping. Preserve originals and hashes before opening; exclude passwords, cookies and credential stores, and do not attempt network resolution. Because the bookmark says BX25 scan copies travelled with the profile refresh, preserve any such copies in their original encrypted form and do not attempt release without the original Risk-desk paper key register or another independently authorized release record. Use the bookmark export's local targets as the profile-search list: incident desk index, desktop-move calendar, oldscan/scanrelease.txt, mug-stock.xls, SEP26 return index, BX25 transfer index, H17-POL-17 renewal ledger, CS-18 loan-set register, staff-groups index, and the PrevERP ledgers only where the original receipt identifiers make them relevant. Within any recovered migration package, also inventory Bundle 06, WN-14, loose desk-note, photo-caption/galley, and print-host/spooler directories as separate objects, preserving original relative paths, timestamps, hashes and omission/deletion metadata. This is a target list, not proof that these directories were part of the profile. Also preserve any Office document cache, AutoRecover/unsaved recovery, temporary workbook copies and recent-file/MRU records relevant to mug-stock.xls or WN-14/Bundle 06, plus Windows thumbnail/preview caches for any photo-caption images. Treat these as recovery leads only; do not resave cached documents or treat a thumbnail/preview as the original. This may recover several separately bookmarked local records, but their presence in the profile is not established. Within any recovered print-host/spooler directory, specifically inventory native PS-0416 and PS-0417 job objects (.SPL/.SHD or equivalent), the queue/port-to-destination map for `bench`, route/driver/firmware metadata, ACK/retry logs, and any associated physical-output/coupon scan or collection record. Treat PS-0416 as a blind control only if its original route is confirmed as the same ESC-N/RECOVER copy path; otherwise retire it.

3. **BX25-08 identity check.** RN-052 identifies FA-17/BX25/08 as a property-annex scan inward transfer. The supplied BX25-08.pdf is a one-page AES-256 encrypted folio with one URI annotation and no embedded image XObject; its content and URI target remain unknown. It may be the drawing, a vector folio or a link/index to another record. Use only the original Risk-desk paper key register for authorized release; do not brute-force or probe an encrypted URI. A prior exploratory derived-setting branch has been withdrawn; do not use or propagate its setting, plaintext or conclusions. Preserve the encrypted original and hash, then inspect title block, metadata and URI target against the MAIL-16 excerpt, H17-POL-17 renewal ledger and the September return index. If unrelated, request the separate drawing by its actual reference.

4. **Conditional native MAIL-16 source/thread retrieval.** The local redacted EML has no In-Reply-To/References headers or native attachment structure, and the custodian says repeated quoted reply material was omitted. However, the incident-date namespace analysis finds that all 20 exported Message-IDs use IR261003 while 15/20 displayed Date headers predate 3 October; original transmission headers are not authenticated. First authenticate the original mail system/namespace and export provenance from the custodian, mailbox inventory, archive index or source manifest. Only then retrieve by authenticated mailbox folder/UID, original Message-ID/thread ID or source record identifier, preserving raw RFC822/MIME, Received/delivery headers, quoted history, attachments and inline images. Do not query using exported identifiers such as mail-16@records.h17.local. The 07:49Z/18:03Z forward-reference is a prepublication excerpt gap, not proof of a real send-time contradiction. If no original namespace/identifier can be authenticated, stop native-thread lookup and treat MAIL-16 as a prepublication excerpt; keep the separate old-drawing request independent. See [incident-date mail namespace analysis](h17-mail-incident-namespace-prepublication-20261104.md) and [prepublication dependency](h17-mail13-mail16-prepublication-dependency-20261104.md).

5. **Competing PS-0417 ticket neighbours.** Request original supplier-index/ledger records and complete packets for **ST-113 (+304 candidate)** and **ST-117 (+300 candidate)**, including posted/unposted/voided/held/reversed/duplicate versions, account/folio, creation/settlement timestamps, work-order attachments, carbonless copies and any explicit PTW/PS cross-reference. These are competing hypotheses, not established mappings. Preserve sequence gaps. The 7 November Critic direction assigns the +300 line to Agent8 and requires original paired-source validation before further offset computation.

6. **Native print-host/device copy-stage artifacts.** After independently identifying host OS and queue/port, preserve the native PS-0417 attempt 1/2/3 and earlier LABEL control. If Windows is confirmed, include original .SPL/.SHD files and metadata, Microsoft-Windows-PrintService/Admin and Operational EVTX, driver/processor/port configuration, device-local job history, retained job buffer and print-completion/media-eject receipt. Preserve the physical ESC-N coupon or retained media separately with chain of custody. ACK remains dispatch evidence, not media-integrity evidence.

7. **AX-7782 object-version gate.** The canonical object ID joins the K04 route, K08 envelope ID and AX-7782 transfer as a locator only. MAIL-13's displayed Date is 2 Oct 09:56Z, before selected PS-0417 ACK2 on 3 Oct 18:02Z, but the 20-message export's incident-date Message-ID namespace means that Date is not authenticated as original send time. The 20:55:10Z receipt_utc is shared by all three COMMIT rows, including a dry-run transfer, so it is not a proven object-version timestamp either. First authenticate the original mail namespace; then obtain the native queue/receipt schema and AX-7782 object manifest/version metadata before treating the 8 MiB payload as a K04 carrier. Independently compare K08 final-phrase authoring time and Bundle-06 inclusion/omission. See [AX-7782 temporal eligibility gate](h17-ax7782-temporal-eligibility-gate-20261107.md) and [incident-date mail namespace analysis](h17-mail-incident-namespace-prepublication-20261104.md).

See also [K04 primary commissioning and drawing source gates](h17-k04-original-commissioning-and-drawing-source-gates-20261107.md). None of these requests supplies missing K04 bytes or K08 words by itself.


### K08: retired-profile native note, mail and search stores (7 November 2026)

The existing retired-profile request should explicitly include the local native stores that can preserve Emily's literal margin/caption wording or complete MAIL-11/MAIL-20 threads. If an authorized retired-profile image or forensic copy exists, acquire read-only with original paths, metadata, hashes and transaction logs:

- Outlook OST/PST and local archive stores, with MAPI profile/configuration metadata, original folder structure, complete message bodies/quoted replies, message and attachment IDs, MIME parts, and attachment/inline-image cache. Include Deleted Items and any preserved recoverable/deleted-message store only where retained and authorized.
- Windows Sticky Notes database `plum.sqlite`, its WAL/SHM files, and containing package directory.
- OneNote local notebooks and cache, including `OneNoteOfflineCache.onecache`, notebook/section files and associated metadata.
- Windows Search ESE index `Windows.edb`, its ESENT transaction/log files, and index scope/catalog configuration. Preserve the index and logs before any rebuild or repair.
- Relevant profile hive/MRU records that identify original WN-14, Bundle 06, desk-note, photo-caption, mug-stock and incident-index paths and last-opened times.
- Per-user printer configuration from `NTUSER.DAT` and `UsrClass.dat`, including printer connections, default printer/device and port settings, PrintHood shortcuts and per-user print preferences; preserve machine `SYSTEM`/`SOFTWARE` hives or equivalent original configuration for queues, ports, drivers, print processors and spooler settings.
- The native spooler `PRINTERS` directory with `.SPL/.SHD` or equivalent objects, PrintService Admin/Operational logs, queue/port history and retained driver/port-monitor packages. Inventory PS-261003-0323 and its 0317/0318/0320/0306 controls separately from PS-0416/PS-0417, preserving job IDs, host/device/port/route, attempts, rendering, media-eject/collection and custody.

The native EML export is only 20 single-part text/plain messages with no MIME attachments. These stores may contain complete thread material, omitted messages, attachments, local note versions, filenames or snippets; their existence and contents are unproven.


Native-mail retrieval keys identified from the export (search these exact local Message-ID tokens in the preserved store): `11.IR261003` (Emily, “RC-17 issue receipt”), `13.IR261003` (Gabriel, “Archive transfer receipt to keep with the folder”), `16.IR261003` (Simon, “Escrow print jobs / recovered buffer”), and `20.IR261003` (Gabriel, “Preservation bundle 06 / desk-caption wording”). The supplied EMLs contain no `In-Reply-To` or `References` headers, so request the native conversation/thread graph, full bodies, quoted/omitted messages, MIME parts, attachment and inline-image IDs.

MAIL-16's route constraint must be preserved during interpretation: ESC-N is the K04 masked-component coupon route; WATCH-SPARE is unrelated; ESC-S is not an input to the K08 keeper's desk phrase. The route transcription maps those queues to jobs 0417, 0420 and 0448 respectively, while job 0323 has no preserved route assignment. Search native mail and profile metadata for job 0323, but do not treat its output as K08 input unless its original route and source role are established.
 Do not access credentials or a live cloud mailbox, and do not rebuild indexes or resave cached documents. Treat this as a local read-only acquisition lead, not evidence that the phrase has been found. It complements the direct print-output locator PS-261003-0323; keep both sources separate until original identifiers establish their relationship.

### K08: conditional photo-caption print witnesses

The note-to-spool sequence crosswalk associates the photo/caption notes N01, N08, N09 and N14 with PS-261003-0301, -0308, -0309 and -0314 respectively. This is an exact suffix/time-sequence association, but no supplied source explicitly states that Nxx maps to job 0300+N, and the jobs' queue/host/device routes are not established. If the original queue/job manifest confirms those pairings, preserve the complete native spool objects and rendered physical outputs for those four jobs, including original document bytes, .SPL/.SHD or native equivalent, job/queue/device/port metadata, attempts, completion/media-eject/collection records and custody. They may retain a printed caption copy or image, but they are 3 October print artifacts, not proof of the pre-1-October original photograph/caption. Keep them separate from the original shared photo-caption archive and from PS-0323's candidate final-envelope output. The 16-byte reconstruction payloads did not directly match note-text digests and are not caption text.

See [the 24-note to spool sequence crosswalk](h17-k08-note-spool-sequence-crosswalk-20261107.md). Do not request or interpret these jobs as K08 inputs unless the native route/job manifest confirms their source role.

### K08: N23 / PS-0323 native print object and rendered output

The 24-note sequence crosswalk maps N23 to PS-261003-0323 (ATTEMPT=1/ACK, CLASS=RECOVER, DEST=store) at the matching 08:55Z five-minute slot. This is a strong structural locator, not a source-explicit route assignment or proof of paper collection. Request the complete native PS-0323 job object and its rendered/printed output: original document/image bytes, .SPL/.SHD or native equivalent, full job record, queue/host/device/port IDs, September route mapping, timestamps, attempt and dispatch records, media-eject/collection evidence, and custody. Preserve controls PS-0317 (N17 standby label), PS-0318 (N18 commissioning label), PS-0320 (N20 semantic brief), and PS-0306 (N06 desk draft) with the same metadata. Preserve N23's original margin/envelope and WN-14/desk-image/galley material separately for literal comparison. MAIL-16's exclusions remain binding: WATCH-SPARE is unrelated and ESC-S is not an input to the K08 phrase; no queue assignment for PS-0323 is established. Do not promote the retained 16-byte log payload to phrase/component status. See [the 24-note to spool crosswalk](h17-k08-note-spool-sequence-crosswalk-20261107.md) and [the custodian acquisition addendum](h17-custodian-acquisition-addendum-20261107.md).


## K08: note-to-spool sequence and candidate final-envelope output (7 November 2026)

The 24 numbered notes N01–N24 align one-to-one with spool jobs PS-261003-0301 through PS-261003-0324. Each matching row is ATTEMPT=1/ACK, with exact five-minute spacing from 07:05 through 09:00 UTC. The strongest candidate final-envelope print record is **PS-261003-0323**: it is the job paired by suffix with N23, Emily's note that the envelope remembers the words she finally put on it, and it is recorded as CLASS=RECOVER, DEST=store.

If an authorized custody path or unsolicited source delivery becomes available, add these exact objects to the existing K08 acquisition scope:

1. **PS-261003-0323**, complete native spool object and rendered physical output, including the original job name, source queue/host/device, attempt/class/destination metadata, original payload, print rendering, completion/media-eject record, collection/receipt evidence and custody.
2. **PS-261003-0317** (N17 standby envelope label, LABEL/store) and **PS-261003-0318** (N18 commissioning envelope label, RECOVER/store) as envelope-label controls.
3. **PS-261003-0320** (N20 semantic line brief, RECOVER/bench) and **PS-261003-0306** (N06 second desk draft, RECOVER/desk) as drafting/desk controls.
4. The original queue manifest or job index proving whether the N01–N24 ↔ 0301–0324 association is causal, plus any missing Bundle 06 trim/omission entries for these jobs.

This is a precise locator and acquisition refinement, not a claim that the reconstructed 16-byte payload contains the phrase. The spool log labels payload integrity unverified, and ACK proves receipt rather than correctness. Keep the existing 21 October custodian channel closed; do not send a new request through it. Preserve the original files and rendered copies without re-encoding.