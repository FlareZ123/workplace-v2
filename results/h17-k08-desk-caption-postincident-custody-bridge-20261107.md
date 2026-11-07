# K08 desk-caption post-incident custody bridge

**Agent 36 · 7 November 2026 · source-derived acquisition lead**

## New observation

Three surviving mail records establish a more specific physical custody question for the exact K08 wording:

| Source | Timestamp | Directly supported fact |
|---|---|---|
| MAIL-14 | 2 Oct 2026, 14:38 UTC | WN-14 was signed; Emily's desk notes were physically under the folder, outside the controlled-copy sleeve; the folder was to be handed to the incoming watch after dinner; photographs and galley captions were kept separate from the engineering procedure. |
| MAIL-18 | 3 Oct 2026, 21:47 UTC | The instrument-store fire was reported contained; the incident team controlled access; nobody was to re-enter for records or personal belongings; the archive appliance and recovery card were destroyed. |
| MAIL-20 | 4 Oct 2026, 11:06 UTC | Gabriel reports that several captions and drafts were on Emily's desk and says the exact words she finally chose matter. The message does not quote the final wording or identify the desk's room. |

MAIL-20 is **13 hours 19 minutes after** the MAIL-18 incident notice. The local export therefore contains a post-incident observation of target-relevant desk material. This is a physical-source locator, not evidence that the final envelope itself was on the desk or that the desk was outside the restricted area.

N23 adds the target-bearing distinction: Emily says the wording in her margin was not an official slogan and that the envelope remembers the words she finally put on it. MAIL-14 supplies the prior physical locator for her desk notes and a named custody transition to the incoming watch.

## Why this changes the K08 acquisition path

The highest-value next step is to reconstruct the **desk and folder custody chain**, rather than infer the final phrase from paraphrases:

1. Obtain the incoming-watch handoff record for the WN-14 folder after dinner on 2 October. Establish the receiving role, time, location, and whether the loose notes physically under the folder travelled with it.
2. Locate Emily's desk and establish whether it was in the instrument store or elsewhere during the 3 October restriction. If it was in the restricted store, request the incident team's property-removal, inventory and return records for the desk contents. If it was outside, identify who had access and who observed the captions/drafts on 4 October.
3. Request the original envelope and the exact margin-bearing sheet or photograph referenced by N23, together with the loose WN-14 desk-note stack, both faces, original order, backing/underlay and any adjacent envelope or print.
4. Request the separate pre-incident crew/galley/noticeboard photograph and caption archive described by MAIL-14 and MAIL-11. Preserve image originals, reverse-side handwriting, caption authorship/revision history, timestamps and folder/album membership.
5. Keep the engineering controlled-copy sleeve, WN-14 folder, loose desk notes, original envelope, and separate photo/caption archive as distinct objects until a physical join is documented.

## Low-confidence accommodation locator

MAIL-17 (3 October 17:31Z) says Emily would be in accommodation after dinner if the watch needed the previous note. Its subject is a valve-gallery concern thread, so this does not prove that the WN-14 folder or caption material was involved. MAIL-19 (4 October 06:22Z) places spare radio chargers at the accommodation desk, and the galley/stores log independently records those chargers being moved there. MAIL-20 later says captions and drafts were on Emily's desk.

This makes the accommodation handover point worth checking, but it does **not** establish that Emily's desk was the accommodation desk or that the incoming watch received the WN-14 folder there. Ask whether the folder/loose notes were handed over or returned in accommodation, and whether the desk in MAIL-20 was the accommodation desk, a briefing-room desk, or a separate workspace. Keep this as a candidate locator only.

## Discriminating outcomes

- **Positive:** an original envelope or margin-bearing source with exact wording and defensible attribution to Emily, linked by custody/version evidence to the final K08 selection. Transcribe the literal text before applying the supplied normalization and HMAC.
- **Useful intermediate:** an authenticated incoming-watch handoff or incident-team property inventory that identifies the desk/folder location and where the original notes or caption folder went.
- **Negative:** the folder/desk material was destroyed or is absent from the custody inventory, or MAIL-20's desk reference cannot be tied to a preserved object. Record that as a bounded source result; do not replace it with a thematic paraphrase.

## Limits

MAIL-14 does not identify the incoming watch by name or give the handoff time. MAIL-18 does not locate Emily's desk or the ESC-N printer. MAIL-20 does not quote the final phrase, state that the original envelope was on the desk, or explain how Gabriel observed the material after the access restriction. Those are the exact custody gaps to resolve.

No phrase candidates were generated or tested. No exact K08 words were recovered. K08 remains MISSING.

## Source SHA-256

- `resources/evidence/mail/14.eml`: `9c86de086a1727ca09b4df6f12cf5c634eaa22a3949424171cc50b4ef9983be5`
- `resources/evidence/mail/18.eml`: `7dc1f122f92ce23c110aa50fd78ae7a471bdf9e60a44e358e3b90e497f664cf0`
- `resources/evidence/mail/20.eml`: `e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71`
- `resources/evidence/crew/noticeboard-and-desk-notes.txt`: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- `resources/evidence/mail/17.eml`: `67493c660dcd08de990c2490af5718072ee9e0991476c0272bf9fff9e96e8014`
- `resources/evidence/mail/19.eml`: `caff45f8c477f9fa6fc5fae0847c9c7f7842ba83c41319c8a47ddace00bd2fbd`
- `resources/evidence/crew/galley-and-stores.log`: `23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46`
