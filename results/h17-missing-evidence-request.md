# H-17 REC8/1: precise request for missing preservation evidence

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

These three leads are grounded in the surviving bookmark, MAIL-14, and print-fleet note. They identify missing originals for custodian retrieval; they add **zero recovered K04 bytes and zero exact K08 words** until the originals are supplied and authenticated.


### K04: Risk transfer index and paper key register

The retired-office bookmark file also points to `file:///R:/Risk/Transfers/BX25/transfer-index.htm`, labelled **"2025 risk scan transfer index"**. The supplier reconciliation independently records `RN-052` as RISK/R1/FILED, asset `FA-17`, folio `BX25/08`, described as a property-annex scan inward transfer; `RN-053` is the LV-42/BX25/12 hired-plant certificate, and `RN-047` is the ST-09/BX25/03 stores-float exception. The bookmark description says the old capture terminal stored BX25 folios with a four-position numeric release setting and that its **paper key register stayed with the Risk desk**.

Request the original BX25 transfer index and a preserved scan/custody record of the Risk desk paper key register, especially the entry for FA-17 / BX25-08 / H17-POL-17/A3. Retain page order, annotations, issue/return entries and provenance. This is a new physical/source locator, **not evidence that the register contains the K04 coupon or that the PDF's release setting is the coupon**.


### K08: electrical-group roster

The same surviving bookmark export lists `file:///R:/IT/staff-groups/EG.htm`, titled **"E.G. electrical group roster"**. Request the preserved original roster, including any embedded photographs, profile links, annotations and file metadata. It may identify the people connected with the night-watch photograph or help locate the retired profile. Its contents are unknown; it does not establish any caption words.

### K04: former finance posting and reversal records

The bookmark export also lists `file:///R:/Finance/PrevERP/posted-items-26.xls` and `file:///R:/Finance/PrevERP/reversal-register.htm`. These may provide an independent original record of the A3 posted versus A4 held-duplicate settlement already summarized in `supplier-reconciliation-L29.csv). Request the original files with workbook formulas, hidden sheets, comments, reversal references and timestamps if they survive. Their relevance to the physical coupon is unproven; they are provenance/version-selection records, not coupon bytes.

### K04: hired-equipment loan-set register

The bookmark `file:///R:/Risk/hired-plant/CS-18/loan-set-register.htm` is titled **"Hired equipment certificates"** and carries a note that LV-series settlement queries were handled at the contractor desk. Request the original register only if it can identify equipment, serials or custody relevant to the incident-period printer/cassette. The connection between CS-18 and FA-17 is currently unestablished, so this is a lower-priority locator.

None of these three files is present in the uploaded ZIP, either repository's current recursive tree, or plausible resource/private paths in v1/v2 Git history. The surviving bookmark is the only located witness. These requests add no K04 bytes and no K08 exact words until an original is supplied and independently authenticated.
