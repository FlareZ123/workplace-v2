# K08: source-authored final caption/version path

**Status:** K08 remains unresolved. This report closes the current note-body phrase-guessing line and identifies the exact source object needed for a complete, verifiable text candidate.

## Question

Can the complete K08 phrase be emitted from the surviving local export by a deterministic source-authored finalization/version operation, rather than by copying a surviving note body or inventing a paraphrase?

## Source evidence

- `evidence/records-custodian.txt` defines K08 as the keeper's personal caption on the **recovery envelope**, used to distinguish it from similarly named commissioning and standby envelopes. It is intended to be memorable, not a cabinet number.
- `evidence/mail/11.eml` explicitly says the final phrase is neither the commissioning label nor the standby-envelope label, and that the wording was worked out from desk notes and **photograph captions**.
- Note N10 in `evidence/crew/noticeboard-and-desk-notes.txt` refers to the photograph "after the last cup". Note N23 says the wording in Emily's margin was not an official slogan and that the envelope remembers the words she finally put on it.
- The surviving note bodies provide semantic context, but no complete final inscription. The bounded direct-adoption check and the recent source-field splice checks did not produce a K08 commitment hit.
- The supplied export contains no original recovery-envelope image/transcription, no original shared photo/caption archive, and no caption sidecar or revision history. The N10→N01 pairing is prior art recorded in `h17-k08-preincident-photo-caption-acquisition-20261107.md`; it is a contextual locator only. The earlier profile/image intake work is recorded in `h17-k08-teal-bit-image-intake-hypothesis-20261116.md` and `h17-profile-refresh-migration-store-retrieval-lead-20261107.md`.

## Source-authored finalization operation

The defensible photo-caption operation is **recover the pre-incident shared photo/caption archive with author and edit attribution intact, then follow an explicit source link from Emily's N10 reference through the caption revision/adaptation to the final recovery-envelope margin**. This is not a free-form assembly of note themes and not simply "take the newest metadata value":

1. Obtain the original shared crew/noticeboard/galley photograph and caption archive, including pre-1 October 2026 material. The existing pre-incident acquisition result pairs N10's "photograph after the last cup" contextually with Jason's N01 empty-bench/finished-tea caption, but expressly treats this as a locator only: it does not prove that N01 and N10 refer to the same physical image or that Emily adopted Jason's caption.
2. Prioritize the original N01 image as a **testable antecedent**, while preserving N02/N06 as Emily-authored exact-language controls. The literal N01 caption has already failed the K08 HMAC and is not the final phrase.
3. Preserve original image files and physical prints (front/back), sidecars, EXIF/IPTC/XMP, album/noticeboard/galley-board membership, original file timestamps, caption text, author/editor identity, revision history, and caption timestamps.
4. Require an explicit source join showing which caption/version Emily used or adapted into the final recovery-envelope wording. Select that source-authored version using its recorded revision order; do not infer it from thematic similarity. Do not substitute the N17 standby or N18 commissioning labels; MAIL-11 excludes them.
5. If the archive does not preserve the final text, use the original recovery envelope itself (or a faithful image/transcription) as the authoritative text source.
6. Apply the exact K08 normalization in `evidence/recovery-routing.json`, compute the prescribed HMAC with the supplied desk nonce, retain the prescribed 16 bytes, and check the unchanged acceptance commitment.

The EXIF/IPTC/XMP/history fields are a **testable extraction surface**, not a claim that the phrase is present in metadata. The original pre-incident photo/caption archive and the physical envelope are distinct source objects; either needs an explicit link to Emily's final margin wording. The source material does not currently identify a unique photo filename or a specific metadata property.

## Conditional source-authored render/copy path: PS-0323

The existing note-to-spool crosswalk supplies a second, more direct candidate for a complete-text construction:

- N23 is Emily's final-margin/envelope note.
- The fixed note/job sequence associates N23 with PS-261003-0323 at 08:55 UTC.
- That row is ATTEMPT=1 / ACK / CLASS=RECOVER / DEST=store.
- The queue note says destination names are physical print destinations, while the crosswalk cautions that queue acceptance does not prove paper collection. No native route/host manifest currently binds PS-0323 to the recovery envelope.

**Conditional operation:** if an authenticated native queue/job manifest confirms that PS-0323 is the recovery-envelope job, recover its original document bytes and rendered output from the native spool object (`.SPL/.SHD` or the host's equivalent) or the retained physical output. Extract the complete printed caption text from that rendered document, not from the 16-byte `PAYLOAD` token. Apply the unchanged K08 normalization and HMAC. This is a concrete source-authored render/copy operation that can emit the whole phrase; the current text reconstruction is not the rendered document.

The PS-0323 16-byte payload itself is not the K08 component: its SHA-256 does not match the K08 slot commitment. Keep PS-0317 (standby label), PS-0318 (commissioning label), PS-0320 (semantic brief), and PS-0306 (desk draft) as controls. PS-0324 is a sequence-aligned label job, not an envelope witness. The note/job association remains structural until the native manifest confirms it.

## Conditional source-authored correspondence-version path

The redacted MAIL-11/MAIL-20 exports are not complete native threads: the supplied EMLs are single-part text/plain, omit usable References/In-Reply-To headers and attachments, and the records-custodian note says repeated quoted reply material was omitted. The incident-date Message-ID tokens in the export are templated/prepublication identifiers, not authenticated native mailbox keys.

If an authorized native mail/archive copy becomes available, first authenticate its namespace and export provenance; then retrieve MAIL-11 and MAIL-20 by verified folder/UID, original Message-ID/thread ID, or authenticated archive record. Preserve raw RFC822/MIME, delivery headers, quoted history, attachments and inline images. Select the final authored caption/version from the complete thread, if present, then apply the unchanged K08 normalization and HMAC. Do not query a live mailbox or native store using the exported templated Message-ID tokens.

This is a source-backed version-history path, not a claim that the missing phrase is present in either thread. The source-specific namespace limitation and timing caveats are documented in `h17-mail-incident-namespace-prepublication-20261104.md`.

## Interpretation and boundary

The available export supports the identity and role of the missing text, and it supports a concrete version-selection procedure if the native caption record is recovered. It does **not** support the exact words. No further phrase grammar, note-ID locator, book scan, or workbook-coordinate branch can supply the missing authored wording without an additional source field.

The retired-profile bookmark paths `R:/IT/desk-images/oldscan/scanrelease.txt` and `R:/IT/desktop-move-2026.html` are contextual leads only. The property annex identifies FA-18 as a network service desk/local archival station, but does not prove that the photograph or caption history is stored there; Agent 50 independently found no source mapping `DEST=bench` to FA-18. Do not infer a storage mapping, reconnect to a protected share, or contact the closed custodian channel.

## Required next input

An independently authorized copy of **any one** of these source objects:

- the original recovery envelope (or a faithful image/transcription of its handwritten caption);
- the original shared crew/noticeboard/galley photo-caption archive (prioritizing the N01 antecedent candidate), with sidecars, author/editor attribution, revision history, and an explicit link to Emily's N10 reference and final envelope wording;
- the native PS-0323 job object plus an authenticated queue/job manifest and rendered output, **only if** that manifest binds the job to the recovery envelope; or
- the authenticated native MAIL-11/MAIL-20 thread(s), including quoted history, attachments and inline images, retrieved only after the original mail namespace is established.

Until one of these source objects is available, K08 must remain unresolved. Do not alter the candidate, commitments, verifier, or normalization rule.

## Confidence

- **High:** K08 is a personal recovery-envelope caption; N17/N18 are excluded; the supplied notes do not state the final inscription.
- **Medium:** the original photograph's caption metadata/version history may preserve the final wording.
- **Low:** FA-18 is the storage location for that photograph or history; the current evidence does not establish this.
