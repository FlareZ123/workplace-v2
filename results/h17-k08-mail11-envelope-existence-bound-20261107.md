# K08 envelope phrase: MAIL-11 text lead and conditional chronology

> **SOURCE CORRECTION (Agent 32, 9 November 2026):** A purported direct MAIL-11 quotation below (“The phrase that matters is the one on the envelope, not the old cabinet labels”) is **not in the original MAIL-11**. The alleged request to separate desk wording from the technical record is also unsupported. The exported message supports editorial intent and excludes the old labels, but does **not authenticate a final physical inscription by its displayed 1 October date**. See [source-audited correction](h17-k08-mail11-source-quote-chronology-correction-20261109.md). The historical analysis below is retained for audit and must be read with this correction.\n\n
**Question.** Does MAIL-11's text, together with its displayed but unauthenticated Date header, support a conditional chronology in which the K08 envelope phrase could predate the AX-7782 receipt field?

## Source facts

The supplied MAIL-11 EML's Date header displays **2026-10-01 18:14:00Z**. This is not yet authenticated as an original transmission time: all 20 exported Message-IDs use the IR261003 namespace, while 15/20 displayed Date headers predate 3 October. Until the original mail namespace and export provenance are authenticated, treat MAIL-11 as a prepublication excerpt rather than a native-timestamped message. Its body states:

- “The desk notes and photograph captions were how I worked out the wording.”
- “The phrase that matters is the one on the envelope, not the old cabinet labels.”
- It asks that the wording remain a separate desk caption rather than being copied into the technical record as a control instruction.

The K08 route in `recovery-routing.json` defines K08 as the keeper's desk phrase for the recovery envelope `H17-IR-261003`; MAIL-20 later identifies the literal final-word carrier as that envelope. AX-7782's transfer ledger has a `receipt_utc` of **2026-10-03 20:55:10Z**. The selected PS-0417 RECOVER ACK2 is dated **2026-10-03 18:02:00Z**.

Calculated differences between the **displayed local record timestamps** (not independently authenticated event/snapshot times):
- MAIL-11 Date header to PS-0417 spool-log timestamp: **47h 48m**
- MAIL-11 Date header to AX-7782 receipt field: **50h 41m 10s**
- PS-0417 spool-log timestamp to AX-7782 receipt field: **2h 53m 10s**

## Interpretation

The custodian note also states that **original mail ordering has been retained by UTC date**. Within that preserved mail-export order, MAIL-11 precedes MAIL-13 and MAIL-14. This supports a relative sequence in which the envelope phrase was already being discussed before the folder-handoff messages, if the unnamed envelope is the later K08 envelope. Treat this as a custodian-declared relative order within the mail corpus, not native authentication of the absolute Date headers or a cross-system timestamp comparison. It does not by itself place the phrase before the PS-0417 spool event or establish the AX-7782 snapshot time.

MAIL-11's **text** is an existence/working-version statement: it distinguishes wording on an envelope from old cabinet labels and says desk notes and photograph captions were used to work it out. If its displayed Date header is authentic, and if the unnamed envelope is the same physical object later identified as `H17-IR-261003`, this would place an envelope phrase before the selected print event and AX-7782 receipt field.

That is only a **conditional chronology inference**. The original mail namespace and export provenance are not authenticated, the AX-7782 receipt field is not an authenticated content-snapshot time, and wording stability is unknown. The text supports a plausible joint-object retrieval hypothesis; it does not yet establish a pre-commit final K08 value.

## Joint physical assembly hypothesis

The surrounding **displayed record chronology** makes a single-folder / envelope-plus-coupon assembly worth testing. These are local export/ledger timestamps, not native-authenticated times or an AX object-version time:

| UTC time | Source event | What it establishes |
|---|---|---|
| 2026-10-01 18:14 (EML Date header) | MAIL-11 | The text refers to the relevant envelope phrase; original transmission time and envelope identity are unverified. |
| 2026-10-02 09:56 (EML Date header) | MAIL-13 | The text says a handoff print was left with the ordinary records folder and identifies AX-7782; original transmission time and actual folder handoff are unverified. |
| 2026-10-02 14:38 (EML Date header) | MAIL-14 | The text says WN-14 was signed and Emily's notes were under the folder; the original transmission time and physical handoff are unverified. |
| 2026-10-03 18:02 (spool-log timestamp) | PS-0417 RECOVER ACK2 | The selected ESC-N spool event is recorded; the local 16-byte payload remains unverified against K04's commitment. |
| 2026-10-03 20:55:10 (receipt_utc field) | AX-7782 ledger | The receipt field postdates the spool-log event by 2h 53m 10s; it is not an authenticated object-version/snapshot time. |
| 2026-10-04 11:06 (EML Date header) | MAIL-20 | The text describes Bundle 06 as staged/trimmed and desk notes as kept with technical material; original transmission time is unverified. |

A plausible physical arrangement is that the K08 phrase is on the recovery envelope and the K04 escrow coupon travelled inside, attached to, or alongside that envelope in the ordinary/WN-14 folder. The timing is compatible with this: the phrase was being discussed by 1 October, the selected coupon print occurred on 3 October, and the AX-7782 receipt field followed later that evening.

This is a **retrieval hypothesis, not a source fact**. K04 and K08 are described as separate source objects; the shared incident identifier does not prove nesting. The displayed mail dates and spool/receipt fields do not establish the actual physical chronology until their native provenance is authenticated. The AX-7782 receipt is not an authenticated content-snapshot time, and MAIL-13/14 do not prove that the two folder descriptions refer to one physical folder.

For physical intake, photograph the folder and envelope before opening or separating anything. Record all faces, flap/seal, adhesive, window, folds, staples, inserts, backing sheets, and relative orientation. Preserve whether the coupon is enclosed, attached, adjacent, or absent. If the envelope is empty or the objects travelled separately, keep the K04 and K08 source chains distinct.

## N23 marginalia as a direct K08 carrier

N23 in `evidence/crew/noticeboard-and-desk-notes.txt` states: “The wording in my margin was never an official slogan. The envelope only remembers the words I finally put on it.” The text export records this statement but does **not** transcribe the actual margin wording. This points to a physical source layer that is absent from the text rendition: the original N23 page and its marginalia may preserve the phrase or a draft/version that can be compared with the envelope.

N23 is undated in the supplied transcription, so it adds no new temporal bound. It does add a direct retrieval target: obtain the original N23 page front and back, full margins and edges, handwriting, erasures/overwriting, inserts/underlays, and page-order context; include any original scan or photograph. Preserve the margin and envelope text as separate versions. The margin may be an intermediate draft, and should not be assumed identical to the final envelope wording.

## PTW-417 photograph as a candidate K08 caption source

A separate source chain makes one specific photograph worth requesting with the K08 materials:

- The retained PTW-417 page says a **cosmetic corrosion photograph was requested**.
- MAIL-04, from Simon to Emily, says the PTW-417 paperwork was reopened for a photograph.
- MAIL-11 says desk notes and photograph captions were used to work out the envelope wording.
- The selected printer job is PS-261003-0417, sharing the 417 identifier with PTW-417.

This is a **candidate cross-source join**, not proof that the PTW-417 photograph is one of Emily's phrase-source photographs. The shared 417 identifier alone is not sufficient. The image may be a technical corrosion record unrelated to the sea/night/table caption themes. MAIL-04 also explains that the paperwork was reopened for the photograph, leaving a later OPEN revision with an old serial. That OPEN revision must remain excluded from K04's signed as-left serial selection, but it may be the very revision carrying the K08-relevant photograph/caption. Preserve its attachment and caption rather than discarding the revision as irrelevant.

Retrieve the complete PTW-417 11-page closeout, all revisions (including the later OPEN revision), field sketch, requested photograph, original caption/metadata, contact sheet and caption register. Preserve image and caption as separate source objects with authorship, date, version and original placement. Compare the caption with Emily's N23 margin and the K08 envelope only after native provenance is established. This may join the K04 PS-0417 closeout/location chain with the K08 photo-caption drafting chain, but no phrase words are currently recovered from it.

## Limits

This does **not** recover any K08 word and does not prove:
1. that MAIL-11's unnamed envelope is the same physical envelope as `H17-IR-261003`;
2. that the displayed Date header is an authentic original transmission time or that the export's Message-ID namespace is original;
3. that MAIL-11's text is a complete native message with no omitted attachments or thread material;
4. that the 1 October wording was already the final wording rather than a draft later revised;
5. that the envelope or its desk-caption source was included in AX-7782;
6. that AX-7782's shared `receipt_utc` is the object's content-snapshot time. The same timestamp appears on other COMMIT rows, including a dry run, so the actual object-version event remains unverified.

The mail export is a single-part text rendition without native threading headers or attachments. First authenticate the original mail namespace and export provenance from the custodian, mailbox inventory, archive index or source manifest; do not use the local synthetic-looking Message-IDs as lookup addresses. Only after that gate passes should native MAIL-11 MIME, full headers, delivery metadata, attachment list/hashes and related thread items be retrieved to test envelope identity and version stability. The original supplier commissioning note may also identify the K08 source object or give a literal example; request its annexes and worked examples without assuming it contains the phrase.

## Next discriminating retrieval

Acquire, in this order:
1. Authenticate the original mail namespace and export provenance using the custodian, mailbox inventory, archive index or source manifest. Do not query by the local synthetic-looking Message-IDs.
2. After that gate passes, retrieve native MAIL-11 and its full thread/attachments, with Message-ID, In-Reply-To, References, received/delivery timestamps, attachment names and hashes.
3. The original supplier commissioning note and all annexes/worked examples that define K08.
4. The physical envelope `H17-IR-261003`, Emily's WN-14 desk-note stack, and separate photo/galley-caption originals, preserving their original placement and version provenance.
5. The AX-7782 original manifest, object-version/snapshot event, and all eight attempt-2 chunk payloads, not only the receipt ledger.

**Confidence:** High that the supplied MAIL-11 text refers to an envelope phrase and desk/photo-caption drafting; low-to-medium that the displayed 1 October Date header is the authentic original transmission time; medium that the unnamed envelope is the later K08 envelope; low that the final wording remained unchanged or was included in AX-7782. No K08 component or combined recovery key was recovered.

**Reproducibility:** Source files `evidence/mail/11.eml`, `evidence/mail/13.eml`, `evidence/mail/14.eml`, `evidence/mail/20.eml`, `evidence/recovery-routing.json`, `evidence/transfers/transfer-audit.jsonl`, and the spool reconstruction log. Time differences were computed from displayed Date/receipt fields and the spool-log timestamp; they are not native-authenticated event times.
