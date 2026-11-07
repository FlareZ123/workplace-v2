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
- **Needed:** an independently retained original coupon, verified 16-byte payload transcript, uncorrupted archival spool/source image, or authoritative printer-side checksum tied to this exact job and ACK attempt. Vendor/property register links `L-29/N` / `FA-17` / `H17-POL-17/A3` / scan `BX25/08` provide provenance only; the supplied scan does not contain the coupon bytes.

## Missing record B: K08 keeper's final caption
- **Owner of remembered wording:** Emily; personal late-watch desk/envelope caption distinguishing the keeper envelope.
- **Problem:** source N02/N06 are marked drafts and N17/N18 are explicitly older standby and commissioning envelope labels. MAIL-11, MAIL-20 and N23 distinguish a final wording that the surviving export does not reproduce.
- **Needed:** the final keeper-envelope label, photograph with legible signed caption, original desk notebook margin, or complete correspondence that records Emily's exact final wording. A thematic paraphrase of the sea, night, lamp, cups or room at the table cannot independently establish the HMAC input.
- **Available check:** the original normalization and HMAC procedure is in `resources/evidence/recovery-routing.json`; the immutable acceptance is `resources/acceptance.json`.

## Source retrieval boundaries
The BX25/08 policy-annex scan points to a Noyes Energy Group website. Public pages provide no incident-archive evidence. Its partner/employee correspondence portal requires a normal account sign-in. The current export provides no account records or credentials. Please supply any additional correspondence as an authorized downloaded export or credentialed source you are entitled to share; do not request an authentication bypass.


## Additional original-source locator
The surviving `retired-office-bookmarks.html` explicitly names `file:///R:/Records/INDEX/IR-261003-H17.txt`, an *original Windows mapped-drive incident desk index*. That source file is **not supplied** with the export. A preserved authorized copy of this exact historical file and the record paths it indexes should be requested from the records custodian. The pointer alone neither establishes the file's original date nor contains missing component bytes. The previous workspace tested four related anonymous public URLs and received 404; the Windows `R:` path is distinct from those URLs. See [predecessor source-addressed intake](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-missing-evidence-intake.md).

## Research-prior-art gate
Predecessor repository [workplace-v1](https://github.com/FlareZ123/workplace-v1/blob/main/results/README.md) contains extensive analysis of the *same original archive*, including [two independent exhaustive three-byte K04 correction sweeps](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-three-byte-bound.md) with **9,285,570,000 variants each and zero match**. A redundant v2 matrix was cancelled after this prior work was discovered. The research frontier remains additional actual K04 source bytes or verbatim K08 words. See [v2 cross-repository gate](h17-v1-prior-art-gate.md).

## Specific offline custody retrieval leads (conditional, no original recovered)

The 2025 property annex assigns **FA-17** to the North printer/cassette and **FA-18** to the network service desk/local archival station; the 4 October fleet note maps `PS-261003-0417` to FA-17. An **already-custodian-authorized, preserved 2026 print-host image**, *if one exists* and independent host records establish a Windows print queue for this job, could contain original `.SHD`/`.SPL` job material or the contemporaneous spool journal at 3 October 18:02 UTC. Completed print jobs are normally removed and neither Windows, retention, FA-18 host status nor snapshot survival is established by the current evidence. Request a historical image and queue provenance from records custody, not live equipment. See [predecessor's source-specific print-host request](https://github.com/FlareZ123/workplace-v1/blob/main/communications/agent12/20261020T0742Z_agent1-historical-print-host-spool-snapshot.md).

The same preserved browser bookmarks refer to `file:///R:/IT/desktop-move-2026.html`, labelled a *Profile-replacement calendar*, as well as `R:/Records/INDEX/IR-261003-H17.txt`. If an authorized **offline image of the 2026 retired desktop profile** survives, its historic `NTUSER.DAT` hive might record `HKEY_CURRENT_USER\\Network\\R` / `RemotePath`, resolving the old mapped-drive namespace. If the mapping was ephemeral, local or SUBST, that key may legitimately be absent. The original migration calendar could help identify the old profile before acquisition. Only an authorized preserved period-appropriate target or record can authenticate missing original index contents. See [predecessor's offline-profile locator analysis](https://github.com/FlareZ123/workplace-v1/blob/main/communications/agent39/20261020T0738Z_agent1-offline-R-drive-target-source.md).

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

MAIL-11's primary subject is **"RC-17 issue receipt"** (Emily, 1 October). It contains an embedded paragraph describing the keeper desk phrase, but should be preserved as a mixed-purpose issue receipt, not reclassified as a dedicated K08 message. MAIL-20 (Gabriel, 4 October, **"Preservation bundle 06 / desk-caption wording"**) is the preservation-bundle message explicitly about the keeper component and its route-sheet normalization/nonce. Keep those roles and dates distinct.

### K08: tea-room stock workbook (contextual lead only)

The surviving `retired-office-bookmarks.html` contains the exact historical local bookmark `file:///R:/Stores/consumables/mug-stock.xls`, labelled **"Tea-room stock sheets"**. That workbook is not in the 46-file local export. N11, MAIL-02 and MAIL-12 independently refer to the chipped blue mugs, window and little lamp. Request the preserved original workbook, if it survives, including hidden sheets, comments, formulas, cell metadata and original file timestamps. This is a **contextual source locator**, not evidence that the workbook contains Emily's final words; do not treat any paraphrase or inferred spreadsheet content as the HMAC input.

### K04: separate monthly consumables return

The 4 October print-fleet retirement note says the rollers and feed brackets were handled on a **separate monthly consumables return**. The supplied `supplier-reconciliation-L29.csv` is the five-ticket L-29/N supplier return-set check; it is not that monthly consumables return and does not establish the physical cassette identity. Request the original monthly return covering the incident-period FA-17/North printer/cassette, its source index, and any associated cassette/lot/serial or media-retention fields. The bookmark `file:///R:/Stores/returns/SEP26/index.htm` is a historical locator to the September returns index, not proof that the relevant monthly return is present there.

The same bookmark describes the September cassette-return index as a **vendor ticket list whose binder pages were signed at the north and south cabinets**. Request the original index together with those signed pages, front and back, and any attached print strips, physical coupons, duplicate receipts, scan/copy records, serials and provenance. Cross-reference the **North** page to L-29/N / FA-17 / H17-POL-17/A3 and the **South** page to L-29/S / LV-42 / CS-18/5. The North page is a possible independent witness for PS-261003-0417; the South page is a possible same-role control for PS-261003-0448 only if its original provenance links the page to that job. Ask explicitly whether either page carries a complete 16-byte physical output or copy receipt. Keep this September index and its signed pages distinct from the separately requested incident-period monthly consumables return: the bookmark proves the locator and the existence of a signing practice, not the pages' contents, incident coverage or survival.

These three leads are grounded in the surviving bookmark, MAIL-14, and print-fleet note. They identify missing originals for custodian retrieval; they add **zero recovered K04 bytes and zero exact K08 words** until the originals are supplied and authenticated.


### K04: Risk transfer index and paper key register

The retired-office bookmark file also points to `file:///R:/Risk/Transfers/BX25/transfer-index.htm`, labelled **"2025 risk scan transfer index"**. The supplier reconciliation independently records `RN-052` as RISK/R1/FILED, asset `FA-17`, folio `BX25/08`, described as a property-annex scan inward transfer; `RN-053` is the LV-42/BX25/12 hired-plant certificate, and `RN-047` is the ST-09/BX25/03 stores-float exception. The bookmark description says the old capture terminal stored BX25 folios with a four-position numeric release setting and that its **paper key register stayed with the Risk desk**.

Request the original BX25 transfer index and a preserved scan/custody record of the Risk desk paper key register, especially the entry for FA-17 / BX25-08 / H17-POL-17/A3. Retain page order, annotations, issue/return entries and provenance. This is a new physical/source locator, **not evidence that the register contains the K04 coupon or that the PDF's release setting is the coupon**.


### K08: electrical-group roster

The same surviving bookmark export lists `file:///R:/IT/staff-groups/EG.htm`, titled **"E.G. electrical group roster"**. Request the preserved original roster, including any embedded photographs, profile links, annotations and file metadata. It may identify the people connected with the night-watch photograph or help locate the retired profile. Its contents are unknown; it does not establish any caption words.

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

This is a separate desk-image locator. The current export establishes the bookmark only; it does **not** establish that the release note contains Emily's margin, a particular photograph, or any K08 wording. Keep it separate from the WN-14 folder, the FA-17 risk ledger, and the RN-052 / BX25/08 property transfer index. Request an offline copy from records custody; do not infer or reuse the PDF's 8131 release code.


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


Also request the original signed PTW-417 work-order or a custodian-certified, privacy-safe signatory/witness crosswalk for the printed initials **S / E**. The current HTML is a records copy and says personal signatures are redacted. Ask whether **E** is the same Emily identified in MAIL-11/MAIL-20, without assuming that identity from an initial. This may establish or falsify a cross-record witness link; it is not itself evidence of the final K08 wording.


The work-order also lists a **cosmetic-corrosion photograph** as requested/outstanding. Ask whether it was taken and, if so, request the original image, caption, metadata/sidecar, and any receipt or link to the field sketch/closeout. Keep it distinct from Emily's desk/galley photographs; the current sources do not establish that this is the K08 photograph or that its caption supplied the final phrase.


**Scoped native-mail addition:** Include the original native `MAIL-04` (Simon to Emily and David, 29 Sep 2026) and only its directly related thread/attachments. It is the retained closeout email that states the B/D/A/C witness walk and is referred to by the PTW-417 work-order; the current text-only export carries no attachment or native thread metadata. Preserve original headers, quoted replies, MIME parts, attachments and any field-sketch/photo link. This is a specific closeout-thread request, not a mailbox-wide search.


## K08: television-room map-back book and tea-receipt bookmark

MAIL-09 (Jason to Zoey, 1 October 2026, 08:03 UTC) records that the library books were in the television room, that the book with a map in the back belonged to David, and that a tea receipt was being used as a bookmark and was deliberately left in place. N23 separately attributes a margin wording to Emily, but does not identify the medium, page, or book. The chronology and shared “margin/bookmark” vocabulary do not prove that Emily wrote in David's book or that the receipt carries her words.

If the physical items survive, request the exact David-owned book and bookmark **together and in situ**. Before moving anything, photograph the cover, spine, title/imprint page, edition/printing statement, copyright page and rear map; record whether the map is bound-in, folded or loose. Photograph the receipt in its original position with the marked spread, then preserve high-resolution images of both sides, folds, marks and any date/merchant/amount or recipe text. Capture the marked page and adjacent pages in full, including page numbers, section headings, complete margins, handwriting, erasures and annotations. Record custody and movement history. Keep “receipt” open to the physical item's actual form; do not infer whether it is a purchase slip or an older recipe/receipt card before inspection.

**Edition caution:** Agent23's *The Way That I Went* is a candidate, not an identified book. A 1939 second edition, revised, is also catalogued as 394 pages with a folded map of Ireland at the rear ([Ulysses Rare Books listing](https://www.rarebooks.ie/books/history/the-way-that-i-went-second-edition-1939/)). Therefore the rear-map clue alone does not identify the 1937 first edition. The physical title/imprint/edition statement is decisive. The apparent alignment of L-29/N ticket numbers 81/94/99/106/112 with *The Volcanic North*, and L-29/S ticket numbers 121/130/135/142/151 with *The Silurian Region*, remains a hypothesis; do not treat ticket IDs as page numbers without an independent original record or a verified page-level mark.

The *Riddle of the Sands* was tested only as a candidate because its public edition contains maps and maritime/night-time motifs. Its pinned printed text yielded zero K08 matches in 55,941 frozen 3–64-word motif-gated windows. MAIL-09 does not name that title. Do not treat it as the identified book or launch another literary-text sweep. The physical book, marked page and receipt are the relevant evidence; no exact K08 words are established by the current export.


### Additional K08 physical identity discriminator: David's pocket book

MAIL-06 (David, 30 September 2026) says an old WN-14 standby transcription is in “my pocket book”; its group D ends `5E67`. MAIL-09 (Jason, 1 October 2026) describes a David-owned map-back book in the television room with a tea receipt left in place as a bookmark. Same owner and close chronology make it worth checking whether these are the same item, but the export never says so. If the map-back book is retrieved, check for the WN-14 standby transcription ending `5E67` as an identity discriminator only; it is not a K08 value and no book-cipher index rule is established.

There is a stronger contextual candidate in *The Riddle of the Sands*, Chapter XX, “The Little Drab Book”. The chapter describes an old cheap-cloth guide for yachtsmen to a British estuary, with a partly scratched “3d.” label, title-page attribution “By Lieut. X--, R.N.”, a yacht-owner frontispiece, and “Dollmann” on the back. The same chapter puts a cabin table, the sea, the end of the night, and discordant voices close together, echoing N20's semantic description. The public edition contains map/chart assets. This may identify the *kind* of book or be a deliberate allusion; it does not identify David's physical copy, and the novel does not say that the in-story guide itself has a map in the back.

The printed text of Chapter XX was tested across all 242,141 contiguous 3–64-word windows with no motif gate; no K08 match was found. The whole-book motif-gated test also found no match in 55,941 windows. If this connection is real, the relevant words are more likely in Emily's handwritten marginalia or on the bookmark than in the printed chapter. When retrieving the physical book, check the Chapter-XX features above, the possible WN-14 `5E67` transcription, the marked page, adjacent pages, all marginalia, and both sides of the receipt. Keep the title and identity as unresolved until the item is inspected.


### Preferred secondary K08 book check: Praeger's *The Way That I Went*

The strongest currently evidenced candidate for MAIL-09's David-owned map-back book is R. Lloyd Praeger's *The Way That I Went: An Irishman in Ireland*, especially the 1947 third edition (416 pages, rear-map-bearing book). In that edition, *The Volcanic North* begins p.62 and *The Silurian Region* p.118. The L-29/N ticket suffixes (81, 94, 99, 106, 112) all fall in the former; the L-29/S suffixes (121, 130, 135, 142, 151) all fall in the latter. In the 1997 reprint, the section boundary is p.111, so p.112 moves to the South section. This is a strong page/section crosswalk, but the supplied records do not say that ticket suffixes are page numbers.

If David's book survives, retrieve the exact copy and receipt together in situ. Record title, edition, publisher/year, pagination and rear folding map; check whether the receipt marks p.112; image p.112 and adjacent pages, all marginalia, and both sides of the receipt. Also check whether the book or any loose insert contains the WN-14 standby transcription with group D ending `5E67` (MAIL-06); that would test whether David's pocket book and MAIL-09's map-back book are the same item. Treat `5E67` as an identity fingerprint only; available rear-map evidence describes “Ireland / Sixty Historical Divisions” and does not support it as a map coordinate.

The 1937 first edition is confirmed as a 394-page volume with a rear folding map, but its section-start pagination was not independently recovered; the 1939 second revised edition pagination also remains unresolved. The 1947 third edition is the strongest checked fit, not a proven unique identification across all editions. The CSV preamble defines R3/R4 as vendor settlement batches, so the ST-112 R3/R4 duplicate is not an edition marker.

This is a secondary physical-carrier request. MAIL-14's placement of Emily's original desk notes under the WN-14 folder remains the primary direct K08 margin-source request. Do not assume Praeger is the title until the physical book is inspected.
