# K08: source-authored final caption/version path

**Status:** K08 remains unresolved. This report closes the current note-body phrase-guessing line and identifies the exact source object needed for a complete, verifiable text candidate.

## Question

Can the complete K08 phrase be emitted from the surviving local export by a deterministic source-authored finalization/version operation, rather than by copying a surviving note body or inventing a paraphrase?

## Source evidence

- `evidence/records-custodian.txt` defines K08 as the keeper's personal caption on the **recovery envelope**, used to distinguish it from similarly named commissioning and standby envelopes. It is intended to be memorable, not a cabinet number.
- `evidence/mail/11.eml` explicitly says the final phrase is neither the commissioning label nor the standby-envelope label, and that the wording was worked out from desk notes and **photograph captions**.
- Note N10 in `evidence/crew/noticeboard-and-desk-notes.txt` refers to the photograph "after the last cup". Note N23 says the wording in Emily's margin was not an official slogan and that the envelope remembers the words she finally put on it.
- The surviving note bodies provide semantic context, but no complete final inscription. The bounded direct-adoption check and the recent source-field splice checks did not produce a K08 commitment hit.
- The supplied export contains no original recovery-envelope image/transcription, no original photograph identified by N10, and no caption sidecar or photo-manager revision history. The earlier profile/image intake work is recorded in `h17-k08-teal-bit-image-intake-hypothesis-20261116.md` and `h17-profile-refresh-migration-store-retrieval-lead-20261107.md`.

## Source-authored finalization operation

The defensible complete-text operation is **version selection from the original caption source**, not a free-form assembly of note themes:

1. Obtain the original photograph referred to by N10, or its native photo-manager record and sidecar.
2. Extract the actual caption field(s), including IPTC/XMP description/title fields and any explicit revision/history entries.
3. Use the source's own revision order to select the final saved caption associated with the recovery-envelope wording. Do not substitute the N17 standby or N18 commissioning labels; MAIL-11 excludes them.
4. If the photo metadata does not preserve the final text, use the original recovery envelope itself (or a faithful image/transcription) as the authoritative text source.
5. Apply the exact K08 normalization in `evidence/recovery-routing.json`, compute the prescribed HMAC with the supplied desk nonce, retain the prescribed 16 bytes, and check the unchanged acceptance commitment.

The IPTC/XMP/history path is a **testable hypothesis**, not a claim that such metadata is present. The physical envelope inscription is the direct authoritative alternative. The source material does not currently identify a filename or a particular metadata property for the photograph.

## Interpretation and boundary

The available export supports the identity and role of the missing text, and it supports a concrete version-selection procedure if the native caption record is recovered. It does **not** support the exact words. No further phrase grammar, note-ID locator, book scan, or workbook-coordinate branch can supply the missing authored wording without an additional source field.

The retired-profile bookmark paths `R:/IT/desk-images/oldscan/scanrelease.txt` and `R:/IT/desktop-move-2026.html` are contextual leads only. The property annex identifies FA-18 as a network service desk/local archival station, but does not prove that the photograph or caption history is stored there. Do not infer a storage mapping, reconnect to a protected share, or contact the closed custodian channel.

## Required next input

An independently authorized copy of **either**:

- the original recovery envelope (or a faithful image/transcription of its handwritten caption); or
- the original N10 photograph plus its native caption sidecar/catalogue record and revision history.

Until one of those source objects is available, K08 must remain unresolved. Do not alter the candidate, commitments, verifier, or normalization rule.

## Confidence

- **High:** K08 is a personal recovery-envelope caption; N17/N18 are excluded; the supplied notes do not state the final inscription.
- **Medium:** the original photograph's caption metadata/version history may preserve the final wording.
- **Low:** FA-18 is the storage location for that photograph or history; the current evidence does not establish this.
