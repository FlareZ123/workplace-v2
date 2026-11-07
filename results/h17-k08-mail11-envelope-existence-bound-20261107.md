# K08 envelope phrase: MAIL-11 pre-commit existence bound

**Question.** Does the local email chronology place the keeper's envelope wording before the 3 October AX-7782 receipt, making the retained object a plausible joint K04/K08 carrier?

## Source facts

MAIL-11 is dated **2026-10-01 18:14:00Z**. Its body states:

- “The desk notes and photograph captions were how I worked out the wording.”
- “The phrase that matters is the one on the envelope, not the old cabinet labels.”
- It asks that the wording remain a separate desk caption rather than being copied into the technical record as a control instruction.

The K08 route in `recovery-routing.json` defines K08 as the keeper's desk phrase for the recovery envelope `H17-IR-261003`; MAIL-20 later identifies the literal final-word carrier as that envelope. AX-7782's transfer ledger has a `receipt_utc` of **2026-10-03 20:55:10Z**. The selected PS-0417 RECOVER ACK2 is dated **2026-10-03 18:02:00Z**.

Calculated intervals:
- MAIL-11 to PS-0417 ACK2: **47h 48m**
- MAIL-11 to AX-7782 receipt: **50h 41m 10s**
- PS-0417 ACK2 to AX-7782 receipt: **2h 53m 10s**

## Interpretation

MAIL-11 is an **existence/working-version statement**: by 1 October, the author was already distinguishing the relevant wording on an envelope from old cabinet labels and said desk notes and photograph captions had been used to work it out. This gives the K08 wording a plausible pre-commit existence bound.

If MAIL-11 refers to the same physical envelope later identified as `H17-IR-261003`, and if its wording remained unchanged, then K08 was temporally eligible to be present in an AX-7782 object captured after 3 October 20:55Z. This strengthens the joint-object retrieval hypothesis.

## Joint physical assembly hypothesis

The surrounding chronology makes a **single-folder / envelope-plus-coupon** assembly worth testing:

| UTC time | Source event | What it establishes |
|---|---|---|
| 2026-10-01 18:14 | MAIL-11 | An envelope phrase was already being treated as the relevant wording; desk notes and photo captions had informed it. |
| 2026-10-02 09:56 | MAIL-13 | A handoff print was left with the ordinary records folder; AX-7782 was identified as the actual retained copy, distinct from drill/dry-run transfers. |
| 2026-10-02 14:38 | MAIL-14 | WN-14 was signed; Emily's desk notes were under the folder, outside the controlled-copy sleeve; the folder was to go to incoming watch after dinner. |
| 2026-10-03 18:02 | PS-0417 RECOVER ACK2 | The selected ESC-N spool event occurred; the local 16-byte payload remains unverified against K04's commitment. |
| 2026-10-03 20:55:10 | AX-7782 receipt ledger | The AX-7782 receipt field postdates the selected print event by 2h 53m 10s. |
| 2026-10-04 11:06 | MAIL-20 | Bundle 06 was described as staged/trimmed; the envelope wording was distinguished from old labels and desk notes were said to be kept with technical material. |

A plausible physical arrangement is that the K08 phrase is on the recovery envelope and the K04 escrow coupon travelled inside, attached to, or alongside that envelope in the ordinary/WN-14 folder. The timing is compatible with this: the phrase was being discussed by 1 October, the selected coupon print occurred on 3 October, and the AX-7782 receipt field followed later that evening.

This is a **retrieval hypothesis, not a source fact**. K04 and K08 are described as separate source objects; the shared incident identifier does not prove nesting. The AX-7782 receipt is not yet an authenticated content-snapshot time, and MAIL-13/14 do not prove that the two folder descriptions refer to one physical folder.

For physical intake, photograph the folder and envelope before opening or separating anything. Record all faces, flap/seal, adhesive, window, folds, staples, inserts, backing sheets, and relative orientation. Preserve whether the coupon is enclosed, attached, adjacent, or absent. If the envelope is empty or the objects travelled separately, keep the K04 and K08 source chains distinct.

## N23 marginalia as a direct K08 carrier

N23 in `evidence/crew/noticeboard-and-desk-notes.txt` states: “The wording in my margin was never an official slogan. The envelope only remembers the words I finally put on it.” The text export records this statement but does **not** transcribe the actual margin wording. This points to a physical source layer that is absent from the text rendition: the original N23 page and its marginalia may preserve the phrase or a draft/version that can be compared with the envelope.

N23 is undated in the supplied transcription, so it adds no new temporal bound. It does add a direct retrieval target: obtain the original N23 page front and back, full margins and edges, handwriting, erasures/overwriting, inserts/underlays, and page-order context; include any original scan or photograph. Preserve the margin and envelope text as separate versions. The margin may be an intermediate draft, and should not be assumed identical to the final envelope wording.

## Limits

This does **not** recover any K08 word and does not prove:
1. that MAIL-11's unnamed envelope is the same physical envelope as `H17-IR-261003`;
2. that the 1 October wording was already the final wording rather than a draft later revised;
3. that the envelope or its desk-caption source was included in AX-7782;
4. that AX-7782's shared `receipt_utc` is the object's content-snapshot time. The same timestamp appears on other COMMIT rows, including a dry run, so the actual object-version event remains unverified.

The mail export is a single-part text rendition without native threading headers or attachments. Native MAIL-11 MIME, full headers, delivery metadata, attachment list/hashes, and related thread items are needed to test envelope identity and version stability. The original supplier commissioning note may also identify the K08 source object or give a literal example; request its annexes and worked examples without assuming it contains the phrase.

## Next discriminating retrieval

Acquire, in this order:
1. Native MAIL-11 and its full thread/attachments, with Message-ID, In-Reply-To, References, received/delivery timestamps, attachment names and hashes.
2. The original supplier commissioning note and all annexes/worked examples that define K08.
3. The physical envelope `H17-IR-261003`, Emily's WN-14 desk-note stack, and separate photo/galley-caption originals, preserving their original placement and version provenance.
4. The AX-7782 original manifest, object-version/snapshot event, and all eight attempt-2 chunk payloads, not only the receipt ledger.

**Confidence:** High that MAIL-11 refers to an envelope phrase by 1 October; medium that it is the same phrase later used for K08; low that the phrase remained unchanged or was included in AX-7782. No K08 component or combined recovery key was recovered.

**Reproducibility:** Source file `evidence/mail/11.eml`; `evidence/recovery-routing.json`; `evidence/transfers/transfer-audit.jsonl`. Time intervals were computed from the three UTC timestamps above.
