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

The claim that a particular network service desk or local archival station was the incident host came from an unauthenticated extraction of the encrypted BX25-08 PDF and is withdrawn. The release setting was obtained by exhaustive search, with no Risk-desk paper-register entry cited. Do not use or propagate any derived PDF content. The current local evidence does not identify a historical print host. Only the original Risk-desk paper key register or another independently authorized release record can authorize access. See the withdrawal notice and corrected source-availability gate.

An **authorized historical print-host image**, *if one exists* and independent host records identify the machine that queued PS-261003-0417, could contain original .SHD/.SPL job material or the contemporaneous spool journal at 3 October 18:02 UTC. Completed print jobs are normally removed; neither Windows, retention nor snapshot survival is established. The unencrypted bookmark to R:/IT/desktop-move-2026.html is a profile-replacement-calendar locator, not proof that the profile or print queue belonged to FA-18. Request the calendar and profile mapping, and identify the host from independent records before prioritizing a whole-system image. If an authorized workstation image is obtained, inventory it for system spooler artifacts (K04) and Bundle 06 / WN-14 / shared photo-caption directories (K08); MAIL-20 and MAIL-14 make this a cross-slot candidate, not proof those materials were stored on a particular machine. Request a historical image and queue provenance from records custody, not live equipment. See [predecessor's source-specific print-host request](https://github.com/FlareZ123/workplace-v1/blob/main/communications/agent12/20261020T0742Z_agent1-historical-print-host-spool-snapshot.md).

If independent host inventory maps a preserved retired profile to the machine that queued PS-261003-0417, preserve both the profile hive for the R: mapping and the full workstation image for possible system spooler artifacts; these are different evidence sources.

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

The same bookmark describes the September cassette-return index as a **vendor ticket list whose binder pages were signed at the north and south cabinets**. Request the original index together with those signed pages, front and back, and any attached print strips, physical coupons, duplicate receipts, scan/copy records, serials and provenance, plus any carbonless duplicate, underlying sheet or transfer copy physically retained with the R3/A3 packet (if present). Do not conflate such a physical underlay with the separate R4/A4 held settlement duplicate. Cross-reference the **North** page to L-29/N / FA-17 / H17-POL-17/A3 and the **South** page to L-29/S / LV-42 / CS-18/5. The North page is a possible independent witness for PS-261003-0417; the South page is a possible same-role control for PS-261003-0448 only if its original provenance links the page to that job. Ask explicitly whether either page carries a complete 16-byte physical output or copy receipt. Keep this September index and its signed pages distinct from the separately requested incident-period monthly consumables return: the bookmark proves the locator and the existence of a signing practice, not the pages' contents, incident coverage or survival.

These three leads are grounded in the surviving bookmark, MAIL-14, and print-fleet note. They identify missing originals for custodian retrieval; they add **zero recovered K04 bytes and zero exact K08 words** until the originals are supplied and authenticated.


### K04: Risk transfer index and paper key register

The retired-office bookmark file also points to `file:///R:/Risk/Transfers/BX25/transfer-index.htm`, labelled **"2025 risk scan transfer index"**. The supplier reconciliation independently records `RN-052` as RISK/R1/FILED, asset `FA-17`, folio `BX25/08`, described as a property-annex scan inward transfer; `RN-053` is the LV-42/BX25/12 hired-plant certificate, and `RN-047` is the ST-09/BX25/03 stores-float exception. The bookmark description says the old capture terminal stored BX25 folios with a four-position numeric release setting and that its **paper key register stayed with the Risk desk**.

Request the original BX25 transfer index and a preserved scan/custody record of the Risk desk paper key register, especially the entry for FA-17 / BX25-08 / H17-POL-17/A3. Retain page order, annotations, issue/return entries and provenance. A prior private note records a release setting obtained by exhaustive search. It is not a register-derived credential and is not authorized. Do not retrieve, use, repeat, or propagate it. Preserve the original encrypted PDF unchanged; only the actual paper-register entry or another independently authorized release record can authorize access. This is a physical/source locator, not evidence that the register contains the K04 coupon or that the PDF password is a REC8 component.


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

There is a stronger contextual clue in *The Riddle of the Sands*, Chapter XX, “The Little Drab Book”. The novel first lists Cowper's *Sailing Tours* among several books in Davies's library, then introduces a separate “particular volume”: an old, cheap-cloth guide for yachtsmen to a British estuary, with a title-page attribution to “Lieut. X--, R.N.”, Dollmann's name on the back, and a yacht-owner frontispiece. This narrative sequence distinguishes the guide from Cowper's book. It supports a yachtsman's estuary-guide profile, but does not identify David's physical copy or prove that the in-story guide is a particular later real-world title. The novel does not explicitly say that this guide has a map in the back. The cabin-table/sea/end-of-night scene also echoes N20, but this is a literary clue, not a recovered K08 phrase.

The printed text of Chapter XX was tested across all 242,141 contiguous 3–64-word windows with no motif gate; no K08 match was found. The whole-book motif-gated test also found no match in 55,941 windows. If this connection is real, the relevant words are more likely in Emily's handwritten marginalia or on the bookmark than in the printed chapter. When retrieving the physical book, check the Chapter-XX features above, the possible WN-14 `5E67` transcription, the marked page, adjacent pages, all marginalia, and both sides of the receipt. Keep the title and identity as unresolved until the item is inspected.


### Alternative K08 page/section crosswalk candidate: Praeger's *The Way That I Went*

Praeger's *The Way That I Went: An Irishman in Ireland* remains an alternative page/section crosswalk candidate, not the leading “Little Drab Book” candidate. It is a natural-history travelogue, whereas the Riddle clue describes a separate yachtsman's guide to a British estuary. The 1947 third edition (416 pages, rear-map-bearing) has *The Volcanic North* beginning p.62 and *The Silurian Region* p.118. The L-29/N ticket suffixes (81, 94, 99, 106, 112) all fall in the former; the L-29/S suffixes (121, 130, 135, 142, 151) all fall in the latter. In the 1997 reprint the boundary is p.111, moving p.112 to the South section. This is a page/section coincidence worth preserving, but the supplied records do not say ticket suffixes are page numbers, and the Riddle clue weakens Praeger's physical-profile fit.

If David's book survives, record its title, edition, publisher/year, pagination and rear folding map before testing this alternative. Check whether the receipt marks p.112 and whether the book or a loose insert contains the WN-14 standby transcription with group D ending 5E67 (MAIL-06). Treat 5E67 as an identity fingerprint only; available rear-map evidence describes “Ireland / Sixty Historical Divisions” and does not support it as a map coordinate. The 1937 first edition is 394 pages with a rear folding map; the 1939 second revised edition pagination remains unresolved. The 1947 third edition is the strongest checked Praeger crosswalk, not a proven unique identification. The CSV preamble defines R3/R4 as vendor settlement batches, so the ST-112 duplicate is not an edition marker.

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

MAIL-09 says the tea receipt was deliberately left in the David-owned map-back book as a bookmark. The retired-office bookmarks also point to `R:/Stores/consumables/mug-stock.xls` (“Tea-room stock sheets”), which is absent from the ZIP. Request that workbook and the original receipt or a source-backed duplicate/transaction trace. Preserve the receipt in situ first; record both sides, date, merchant, amount, and any handwritten marks before attempting a join. Use the former-system `posted-items-26.xls` or `reversal-register.htm` only if the receipt's own identifiers make those records relevant. Do not assume the unrelated RN-047 stores-float exception is this receipt.


## K08: conditional underleaf indentation examination

MAIL-14 locates Emily's loose desk notes under the WN-14 folder, outside the controlled-copy sleeve; N23 places the finally chosen wording in Emily's margin. If she wrote that margin while another sheet, pad leaf, folder insert or backing sheet was underneath, the lower paper may retain latent writing-pressure indentations even if the visible margin or photograph is missing. The surviving export does not establish that an underlay was present at the time of writing or that any impression survives.

If an authorized original-paper set becomes available, preserve the WN-14 folder, loose notes, adjacent pad leaves, folder backing/inserts and envelope backing sheets **in their original order and orientation**. Photograph every surface and both faces before movement or specialist processing. Do not rub, shade, pencil over, flatten, clean or chemically process the papers. Refer the originals to a qualified forensic document examiner for assessment under the applicable document-indentation standard; the examiner should decide whether optical side-lighting and/or EDD/ESDA is appropriate. EDD can affect pencil marks, so documentation must precede any such examination. Preserve raw images, settings, any lifts, hashes and an independent verbatim transcription.

A positive K08 result requires a legible inscription independently attributed by physical context and chronology to Emily's **final incident-envelope margin**. An impression of N02/N06 draft wording, N17/N18 decoy labels or unrelated notes is not K08. Apply the unchanged K08 normalization/HMAC only after source attribution. A negative examination applies only to the specific sheets examined. This is a conditional acquisition modality, not evidence that an underlay existed or that any exact words have been recovered. See [K08 underleaf-indentation acquisition path](h17-k08-underleaf-indentation-acquisition-20261107.md) and the [NIST/OSAC ANSI/ASB 044-19 standard record](https://www.nist.gov/osac/standards-library/ansiasb-standard-044-19).


## 7 November 2026: request both competing ST↔PTW↔PS index mappings

A later source-derived audit identifies two plausible numeric offsets between the five posted FA-17 L-29/N service tickets and the same-suffix PTW/PS records. **Neither is an authenticated crosswalk.** The +304 mapping has stronger controls in the surviving export (four matched North tickets land in bays A/B/C/D in binder order, and the earlier FA-17 L-28 holdout matches 2/2 rather than 1/2 for +300), but the original September index or a paired original ticket is still required. Do not retrieve only the +300 set, and do not promote +304 to fact.

| Ticket / source group | +300 candidate PTW / PS | +304 candidate PTW / PS |
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

The +304 audit's four North matches, four distinct bays, binder-order alignment, and 2/2 South holdout are evidence for prioritizing that candidate set during retrieval. They are still a pattern inferred from the supplied records. The +300 candidate remains listed because it is a live competing explanation and the original index is absent. The shared cassette, asset and folio links establish a cohort/provenance association, not an individual ticket-to-job pair. See the reproducible offset audit (h17-k04-st-ptw-ps-offset-ambiguity-20261107.md) and the current source synthesis (results/README.md).



## HST-4 historian sequence continuation and sample-to-job index

The supplied HST-4 freeze sample is explicitly incomplete and says acquisition was interrupted at 21:14. It contains 145 JSONL records: 112 PV records with sequence numbers 100–211, plus 33 DIAG_WORD records (raw_u16) across sequence numbers 0–7 and multiple revisions. No record in the supplied sample has sequence 212–227.

A source-derived audit finds that all 112 retained PV sequence numbers 100–211 align arithmetically with the first 112 spool jobs PS-261003-0300 through PS-261003-0411 under the candidate relation job suffix = PV seq + 200. If that relation continues, missing seq 212–227 would align with PS-261003-0412 through PS-261003-0427, including **seq 217 ↔ PS-261003-0417**. This is a promising independent index hypothesis, not an authenticated sample-to-job mapping. Simple fixed-gap PV-to-random mappings have already failed printer-only parity; do not treat the +200 alignment as proof of a shared generator or draw count.

If an authorized new custody path or unsolicited delivery becomes available, request the **complete native HST-4/HST-4 historian export**, specifically preserving:

1. Every record for seq 212–227, with seq 217 prioritized but the whole interval retained as a holdout-capable block.
2. The original definition of the seq field and the source-authenticated sample-to-job cross-reference, including the rule that produced the observed 100–211 / PS-0300–0411 alignment.
3. Original acquisition order, timestamps with their recorded UTC offsets, tag, field, unit, quality, state, revision, and any freeze/interleave metadata. Do not deduplicate revisions or discard SUSPECT/RUN/HOLD rows.
4. All PV and DIAG_WORD records, including raw_u16 values and their revision/quality semantics, plus the native export header, interruption/restart log, and any adjacent records before/after the 21:14 interruption.
5. The source system's audit trail identifying who exported the sample, the query/time window, and whether the missing seq range was excluded, never acquired, or lost during preservation.

The existing crosswalk report is h17-hst4-pv-spool-job-crosswalk-20261107.md. The supplied sample's 112/112 arithmetic alignment is a useful retrieval locator; only the original HST-4 index or a paired native record can authenticate it.


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

2. **Old supplier drawing named in MAIL-16.** Obtain the original drawing, all sheets/revisions/legend/part lists, title block, issue date, supplier, model/serial identifiers and custody. MAIL-16 says ESC-S also appears on it, while the September label transcription is current and the August service mapping must not replace it. Obtain the September current transcription and August mapping separately as version controls. Do not infer the physical meaning of “catch” before the drawing identifies the part.

3. **BX25-08 identity check.** RN-052 identifies FA-17/BX25/08 as a property-annex scan inward transfer. The supplied BX25-08.pdf is a one-page AES-256 encrypted folio with one URI annotation and no embedded image XObject; its content and URI target remain unknown. It may be the drawing, a vector folio or a link/index to another record. Use only the original Risk-desk paper key register for authorized release; do not brute-force or probe an encrypted URI. Preserve the encrypted original and hash, then inspect title block, metadata and URI target against MAIL-16, H17-POL-17 renewal ledger and the September return index. If unrelated, request the separate drawing by its actual reference.

4. **Full native MAIL-16 thread.** The local redacted EML has no In-Reply-To/References headers or native attachment structure, and the custodian says repeated quoted reply material was omitted. Obtain the entire native conversation, parent/child messages, Received/delivery headers, quoted history, MIME boundaries, attachments and inline images. The omitted history may identify the old supplier drawing's title, revision, location or attachment. If no additional reference exists, close this locator.

5. **Competing PS-0417 ticket neighbours.** Request original supplier-index/ledger records and complete packets for **ST-113 (+304 candidate)** and **ST-117 (+300 candidate)**, including posted/unposted/voided/held/reversed/duplicate versions, account/folio, creation/settlement timestamps, work-order attachments, carbonless copies and any explicit PTW/PS cross-reference. These are competing hypotheses, not established mappings. Preserve sequence gaps. The 7 November Critic direction assigns the +300 line to Agent8 and requires original paired-source validation before further offset computation.

6. **Native print-host/device copy-stage artifacts.** After independently identifying host OS and queue/port, preserve the native PS-0417 attempt 1/2/3 and earlier LABEL control. If Windows is confirmed, include original .SPL/.SHD files and metadata, Microsoft-Windows-PrintService/Admin and Operational EVTX, driver/processor/port configuration, device-local job history, retained job buffer and print-completion/media-eject receipt. Preserve the physical ESC-N coupon or retained media separately with chain of custody. ACK remains dispatch evidence, not media-integrity evidence.

7. **AX-7782 object-version gate.** The canonical object ID joins the K04 route, K08 envelope ID and AX-7782 transfer as a locator only. MAIL-13 is dated 2 Oct 09:56Z, before selected PS-0417 ACK2 on 3 Oct 18:02Z. The 20:55:10Z receipt_utc is shared by all three COMMIT rows, including a dry-run transfer, so it is not yet a proven object-version timestamp. Obtain native MAIL-13, receipt/queue schema and AX-7782 object manifest/version metadata before treating the 8 MiB payload as a K04 carrier; independently compare K08 final-phrase authoring time and Bundle-06 inclusion/omission. See [AX-7782 temporal eligibility gate](h17-ax7782-temporal-eligibility-gate-20261107.md).

See also [K04 primary commissioning and drawing source gates](h17-k04-original-commissioning-and-drawing-source-gates-20261107.md). None of these requests supplies missing K04 bytes or K08 words by itself.
