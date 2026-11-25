# K08: source-authored final caption/version path

**Status:** K08 remains unresolved. This report closes the current note-body phrase-guessing line and identifies the exact source object needed for a complete, verifiable text candidate.

## Question

Can the complete K08 phrase be emitted from the surviving local export by a deterministic source-authored finalization/version operation, rather than by copying a surviving note body or inventing a paraphrase?

## Source evidence

- `evidence/records-custodian.txt` defines K08 as the keeper's personal caption on the **recovery envelope**, used to distinguish it from similarly named commissioning and standby envelopes. It is intended to be memorable, not a cabinet number.
- `evidence/mail/11.eml` explicitly says the final phrase is neither the commissioning label nor the standby-envelope label, and that the wording was worked out from desk notes and **photograph captions**.
- `evidence/mail/14.eml` says the WN-14 folder was handed to the incoming watch, Emily's desk notes were **under** the folder (not inside the controlled-copy sleeve), a pencil standby transcription had been crossed through, and the photographs/galley captions were kept separate from the engineering procedure.
- Note N10 in `evidence/crew/noticeboard-and-desk-notes.txt` refers to the photograph "after the last cup". N23's surviving transcription says the wording was in Emily's margin and that the envelope remembers the words she finally put on it; it does **not** transcribe the margin wording itself. The original N23 sheet is therefore a priority source object, not a phrase candidate.
- The surviving note bodies provide semantic context, but no complete final inscription. The bounded direct-adoption check and the recent source-field splice checks did not produce a K08 commitment hit.
- The supplied export contains no original recovery-envelope image/transcription, no original shared photo/caption archive, and no caption sidecar or revision history. The N10→N01 pairing is prior art recorded in `h17-k08-preincident-photo-caption-acquisition-20261107.md`; it is a contextual locator only. The earlier profile/image intake work is recorded in `h17-k08-teal-bit-image-intake-hypothesis-20261116.md` and `h17-profile-refresh-migration-store-retrieval-lead-20261107.md`.

## Source-authored finalization operation

The strongest source-authored version operation is to reconstruct the **WN-14 desk-note edit chain** and join it to the separate photo/galley-caption archive and the final recovery envelope. This is not a free-form assembly of note themes and not simply "take the newest metadata value":

1. Obtain the original N23 note sheet and the WN-14 folder/Emily's loose desk-note stack in original order. MAIL-14 places the notes **under** the folder, outside the controlled-copy sleeve, and says a pencil standby transcription had been crossed through. The current N23 transcription describes a margin but omits its actual wording. Preserve the crossed-through pencil note, the complete N23 margin, every other margin edit, reverse sides, inserts, adjacent pad leaves, folder/envelope backing sheets, physical order and any pressure/indentation evidence. If the visible margin is incomplete, retain the whole paper grouping for a qualified forensic document examiner to assess latent indentations under the documented [underleaf-indentation path](h17-k08-underleaf-indentation-acquisition-20261107.md); document optically before any EDD/ESDA, and do not attempt rubbing, shading or chemical processing locally.
2. Obtain the separate original shared crew/noticeboard/galley photograph and caption archive, including pre-1 October 2026 material, with author/editor attribution and revision history intact. MAIL-14 explicitly says these photographs and galley captions were kept separate from the engineering procedure.
3. N10's "photograph after the last cup" is contextually paired in prior art with Jason's N01 empty-bench/finished-tea caption, but this is only an antecedent locator: it does not prove N01 and N10 refer to the same physical image or that Emily adopted Jason's caption. Preserve N02/N06 as Emily-authored exact-language controls; the literal N01 caption has already failed the K08 HMAC and is not the final phrase.
4. Require a source-visible edit/version chain from the original photo-caption or desk-note source, through Emily's margin edits, to the exact wording copied onto the recovery envelope. Select the final authored version using its recorded order/markup; do not infer it from thematic similarity. Do not substitute the N17 standby or N18 commissioning labels; MAIL-11 excludes them. The crossed-through pencil standby transcription in WN-14 is a distinct source object and must not be conflated with the N17 standby-envelope label.
5. If the folder/desk-note/photo archive does not preserve the final text, use the original recovery envelope itself (or a faithful image/transcription) as the authoritative text source.
6. Apply the exact K08 normalization in `evidence/recovery-routing.json`, compute the prescribed HMAC with the supplied desk nonce, retain the prescribed 16 bytes, and check the unchanged acceptance commitment.

EXIF/IPTC/XMP/history fields are a **testable extraction surface**, not a claim that the phrase is present in metadata. The WN-14 desk-note stack, pre-incident photo/caption archive and physical envelope are distinct source objects; the recovered material must explicitly connect Emily's final margin wording to the envelope inscription. The source material does not currently identify a unique photo filename or a specific metadata property.

## Conditional source-authored render/copy path: PS-0323

The existing note-to-spool crosswalk supplies a second, more direct candidate for a complete-text construction:

- N23 is Emily's final-margin/envelope note.
- The fixed note/job sequence associates N23 with PS-261003-0323 at 08:55 UTC.
- That row is ATTEMPT=1 / ACK / CLASS=RECOVER / DEST=store.
- The queue note says destination names are physical print destinations, while the crosswalk cautions that queue acceptance does not prove paper collection. No native route/host manifest currently binds PS-0323 to the recovery envelope.

**Conditional operation:** if an authenticated native queue/job manifest confirms that PS-0323 is the recovery-envelope job, recover its original document bytes and rendered output from the native spool object (`.SPL/.SHD` or the host's equivalent) or the retained physical output. Extract the complete printed caption text from that rendered document, not from the 16-byte `PAYLOAD` token. Apply the unchanged K08 normalization and HMAC. This is a concrete source-authored render/copy operation that can emit the whole phrase; the current text reconstruction is not the rendered document.

The PS-0323 16-byte payload itself is not the K08 component: its SHA-256 does not match the K08 slot commitment. Keep PS-0317 (standby label), PS-0318 (commissioning label), PS-0320 (semantic brief), and PS-0306 (desk draft) as controls. PS-0324 is a sequence-aligned label job, not an envelope witness. The note/job association remains structural until the native manifest confirms it.

For a recovered native print object, reuse the existing bounded read-only parsers: `work/h17_emf_text.py` for EMF/EMFSPOOL, `work/h17_xps_text.py` for XPS/OXPS UnicodeString runs, and `work/h17_xps_glyph_indices.py` for XPS glyph-index-only runs where UnicodeString is absent. Preserve the original spool bytes and the extractor's coverage/status. These tools do not recover bitmap-only or outline-only text; an empty/incomplete extraction is not a complete negative. Use the historical renderer and/or OCR only when the native text records do not contain the caption.

## Conditional shared ESC-N print-object path: PS-0417 attempt-1 LABEL

A second cross-slot print-object path is worth retaining separately from the N23→PS-0323 sequence locator; its physical target remains unresolved:

- The records-custodian note defines K08 as the personal caption used to distinguish the recovery envelope from similarly named commissioning and standby envelopes. MAIL-20 makes the final words on the recovery-envelope face authoritative.
- MAIL-16 explicitly excludes ESC-S from the keeper phrase but does not establish whether ESC-N carries the wording. The incident-date route transcription maps ESC-N to PS-261003-0417.
- The retained spool reconstruction has a 16:45Z `LABEL/ACK` row for PS-0417, followed by 18:01Z `RECOVER/REQUESTED`, 18:02Z `RECOVER/ACK`, and 18:03Z `RECOVER/REQUESTED`. The K04 rule selects the 18:02Z RECOVER ACK; the earlier LABEL is not a K04 input.
- PS-0417 is the only retained same-JOB `LABEL/ACK → RECOVER` sequence. PS-0420 is a useful control with `STORES/ACK → RECOVER/ACK`, and MAIL-16 explicitly identifies WATCH-SPARE as unrelated. This control prevents treating multi-class same-JOB behavior alone as an envelope link; PS-0417's LABEL class remains a distinct but unverified carrier clue.
- MAIL-14 and N23 distinguish the WN-14 folder sticker from the recovery-envelope inscription: the spare sticker was only a dispatch number, while the final words Emily chose belong on the recovery envelope; photos and galley captions were kept outside the WN-14 sleeve. The PS-0417 LABEL could be a dispatch-number print of that kind or another object, but it cannot be equated with the specific sticker removed on 2 Oct without a print-to-object link; it remains distinct from the final envelope words. MAIL-17's 17:31Z body only says Emily would be in accommodation after dinner if the watch needed the previous note; it does not mention an envelope or a print label. It therefore provides no temporal or placement support for a PS-0417 LABEL-to-recovery-envelope link. Keep the output-to-object identity unresolved pending native media or a contemporaneous placement record.
- If the sequence-only N23→PS-0323 association is correct, its 08:55Z margin/draft locator precedes the PS-0417 16:45Z LABEL row, making the latter a plausible subsequent print stage only. That crosswalk is not an authenticated foreign key, and neither chronology nor LABEL class proves the label was attached to the recovery envelope.

**Conditional operation:** if an independently authorized native PS-0417 LABEL object is recovered, preserve its original document and native spool object (`.SPL/.SHD` or host equivalent), queue/job manifest, driver/processor/port metadata, all attempt/class records, rendered output, physical collection/affix witness and custody. First establish whether the output was the WN-14 dispatch sticker, a label attached to the recovery envelope, or another object. If it is the WN-14 sticker, record its dispatch number only; do not test it as the K08 phrase. Only if a contemporaneous source/physical witness binds the output to the recovery-envelope face should its complete text (not the 16-byte PAYLOAD token) be evaluated with the unchanged K08 normalization and HMAC. Keep the 18:02Z RECOVER object separate for K04 and PS-0420 as a negative control. The raw EMF glyph-index intake in `work/h17_emf_glyph_index_intake.py` now passes synthetic controls for EXTTEXTOUT, POLYTEXTOUT, SMALLTEXTOUT, exact metadata-only spool binding, invalid offsets, no-header input, malformed/unsupported EMF+ glyph records, and an EMF page embedded after a native-spool byte prefix (`work/test_h17_emf_glyph_index_intake.py`). It is not a renderer or Unicode glyph-map recovery tool; EMF+ glyph-index content remains explicitly incomplete. Existing bounded EMF/XPS parsers and the K08 image/OCR intake can be reused; do not build a duplicate renderer or scanner.

This is a source-grounded **acquisition hypothesis**, not a complete-text constructor from the current export. No native PS-0417 media object, rendered page, queue manifest or output-to-envelope witness is present. The 16-byte LABEL payload is not the phrase; a same-JOB identifier, class label, route or time sequence alone does not authenticate the final inscription. Keep this path distinct from PS-0323 until a source manifest or physical envelope association joins them.

## Conditional source-authored correspondence-version path

The redacted MAIL-11/MAIL-20 exports are not complete native threads: the supplied EMLs are single-part text/plain, omit usable References/In-Reply-To headers and attachments, and the records-custodian note says repeated quoted reply material was omitted. The incident-date Message-ID tokens in the export are templated/prepublication identifiers, not authenticated native mailbox keys.

If an authorized native mail/archive copy becomes available, first authenticate its namespace and export provenance; then retrieve MAIL-11 and MAIL-20 by verified folder/UID, original Message-ID/thread ID, or authenticated archive record. Preserve raw RFC822/MIME, delivery headers, quoted history, attachments and inline images. Select the final authored caption/version from the complete thread, if present, then apply the unchanged K08 normalization and HMAC. Do not query a live mailbox or native store using the exported templated Message-ID tokens.

This is a source-backed version-history path, not a claim that the missing phrase is present in either thread. The source-specific namespace limitation and timing caveats are documented in `h17-mail-incident-namespace-prepublication-20261104.md`.

## Interpretation and boundary

The available export supports the identity and role of the missing text, and it supports a concrete version-selection procedure if the native caption record is recovered. It does **not** support the exact words. No further phrase grammar, note-ID locator, book scan, or workbook-coordinate branch can supply the missing authored wording without an additional source field.

The retired-profile bookmark paths `R:/IT/desk-images/oldscan/scanrelease.txt` and `R:/IT/desktop-move-2026.html` are contextual leads only. Any FA-18 description obtained by locally decrypting BX25-08 is exploratory content, not authenticated by the Risk-desk paper key register and not authoritative for host identity or storage mapping. Agent 50 independently found no source mapping `DEST=bench` to FA-18. Do not infer a storage mapping, reconnect to a protected share, or contact the closed custodian channel.

## Required next input

An independently authorized copy of **any one** of these source objects:

- the original recovery envelope (or a faithful image/transcription of its handwritten caption);
- the original N23 note sheet and WN-14 folder/Emily's loose desk-note stack in original order, including the crossed-through pencil standby transcription, complete margin wording, reverse sides, inserts, adjacent pad leaves, folder/envelope backing sheets and any source-visible edit/version chain; preserve originals for qualified indentation examination if appropriate;
- the original shared crew/noticeboard/galley photo-caption archive (prioritizing the N01 antecedent candidate), with sidecars, author/editor attribution, revision history, and an explicit link to Emily's N10 reference and final envelope wording;
- the native PS-0323 job object plus an authenticated queue/job manifest and rendered output, **only if** that manifest binds the job to the recovery envelope; or
- the authenticated native MAIL-11/MAIL-20 thread(s), including quoted history, attachments and inline images, retrieved only after the original mail namespace is established.

Until one of these source objects is available, K08 must remain unresolved. Do not alter the candidate, commitments, verifier, or normalization rule.

## Confidence

- **High:** K08 is a personal recovery-envelope caption; N17/N18 are excluded; MAIL-14 places Emily's desk notes under WN-14 and separates the photo/galley captions from the engineering procedure; the supplied text export does not state the final inscription.
- **Medium:** the original WN-14 desk-note margins and separate photo-caption revision history may preserve the authored edit chain to the final wording.
- **Low:** any FA-18 storage relationship; the locally decrypted property-PDF content is not paper-register-authenticated and does not establish a host/storage mapping.
