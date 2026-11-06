# K08 object-provenance boundary: keeper's desk-margin caption

**Date:** 2026-11-06  
**Owner:** Agent 5  
**Status:** Source-derived object classification; exact wording still MISSING.

> **Correction to the first draft:** MAIL-11 is the RC-17 revision-C issue receipt, not a K08 message. The earlier draft incorrectly attributed the old-label distinction to MAIL-11. This corrected version removes that claim and relies on the actual K08 sources below.

## Finding

The strongest supported interpretation is that K08 is the **keeper's caption for the spirit of the late watch**, copied from Emily's desk margin onto the envelope. It is a distinct desk-caption object, separate from the WN-14 engineering controlled-copy material. The records establish the semantic brief and normalization rule, but do not identify which surviving text, if any, is the final wording. The export is explicitly incomplete, so direct reuse, a light edit, and a new line remain open possibilities; the exact K08 commitment is the acceptance check.

This does **not** prove whether the final caption was a revision of an earlier scene caption or a standalone new sentence. In particular, N13 is an authentic Emily scene caption, but no source identifies it as the final wording's ancestor.

## Source evidence

- **Records-custodian note, lines 4–8 and 10–22:** This is a working preservation export, not the full incident record; repeated quoted reply material is omitted, and the absence of a gap marker is not a completeness certificate. It defines K08 as the keeper's desk phrase: a personal caption distinguishing the recovery envelope from similarly named commissioning and standby envelopes, intentionally memorable rather than a cabinet number. It also warns that a source reference does not make every byte in that record part of the recovery envelope.
- **K08 route entry:** The source is explicitly “keeper's desk phrase, crew notes and noticeboard drafts.” Its rule says to recover the keeper's caption for the spirit of the late watch rather than the technical incident title, then apply the specified normalization and HMAC check.
- **MAIL-20, lines 12–22:** The bundle is trimmed and has no mailbox search or live facility connection. Gabriel says Emily's description concerned the late crew making room for one another, rather than an accurate description of a valve or the fire. There were several captions and drafts on her desk; the exact words she finally chose matter more than a paraphrase. The acceptance check distinguishes candidates, and the route sheet supplies normalization and desk nonce.
- **MAIL-14, lines 12–23:** WN-14 was signed using four ink groups A–D. The pencil note was a standby transcription and was crossed through; the spare dispatch sticker was removed so it would not be mistaken for a control group. Emily's desk notes were under the folder, outside the controlled-copy sleeve. David explicitly says the photographs and galley captions should not be filed as part of the engineering procedure.
- **N20, line 62:** Emily's stated semantic brief is the sea, the end of the night, and voices at the table. She explicitly says not to use the shorter standby label.
- **N23, line 71:** Emily says the wording in her margin was never an official slogan and that the envelope preserves the words she finally put on it.
- **N17 and N18:** These are identified in the notes as standby and commissioning envelope labels. N20 explicitly rejects the standby label. The commissioning label is a distinct source object; no evidence establishes it as the keeper's final caption.
- **N13, line 41:** This is an authentic Emily scene caption about mugs, a window, and the lamp at the end of the night. It is useful author/context evidence, but no source says it is the final envelope wording.

## Interpretation and implications

1. Treat K08 as the **keeper's late-watch caption copied from Emily's desk margin to the envelope**.
2. Keep WN-14 control groups, the crossed-through standby transcription, and the spare dispatch sticker outside the K08 candidate source. They belong to a separate engineering controlled-copy workflow.
3. Treat N17 as an explicitly rejected standby label. Treat N18 as a commissioning label with a different recorded purpose; do not silently promote either label to the keeper's final wording.
4. Use the photo captions and everyday desk notes as semantic and author-style evidence. Keep N13 as one author sample; do not assume a direct N13-to-envelope revision chain without evidence.
5. Preserve the source brief (late crew making room, sea/water outside, night nearly finished, voices at a table) while requiring exact whole-caption generation and the original K08 acceptance check.
6. Do not report a paraphrase, a plausible-sounding sentence, or a generated candidate as recovered. The exact text remains unknown.

## Source pins

- `evidence/records-custodian.txt`: SHA-256 `786211e7be248e6ba31f017a071e038436782b8550b863f85d77a6c32e1d640a`
- `evidence/mail/20.eml`: SHA-256 `e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71`
- `evidence/mail/14.eml`: SHA-256 `9c86de086a1727ca09b4df6f12cf5c634eaa22a3949424171cc50b4ef9983be5`
- `evidence/crew/noticeboard-and-desk-notes.txt`: SHA-256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- `evidence/recovery-routing.json`: SHA-256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`

No candidate phrase or acceptance digest was used to derive this provenance interpretation.

## Candidate-generation consequence

Because the custodian explicitly says repeated quoted reply material is omitted and the export is not a completeness certificate, the final prompt must not assume the keeper caption is novel or prohibit verbatim reuse. Direct reuse, a light edit, and new wording remain open. The Agent8 base final prompt was corrected on 6 November to include the custodian note and K08 route source/rule and to preserve this version uncertainty.

- Exact-control candidate streams: workflow run `42249717424` (cases 2, 6, 17, 18 remain the useful controls; its case-0 job was cancelled before producing a result).
- Version-neutral final candidate stream: workflow run `42251003805`, using the corrected prompt and original K08 acceptance check.

These runs are pending; this report makes no claim that a candidate has been recovered.

## Direct test of surviving note captions

Using the exact K08 verifier path (route normalization, HMAC-SHA256 keyed by the decoded desk nonce truncated to 16 bytes, then SHA-256 against the K08 slot digest), all 24 N01–N24 note lines were tested as direct candidates. **0/24 matched.** This rules out verbatim reuse of one of the current note lines. It does not rule out a direct reuse of an omitted reply quotation or another desk draft, because the custodian explicitly says the export is incomplete.

Reproducer: `agents/agent5/k08_note_direct_commitment_check.py`  
Source pins: `acceptance.json` SHA-256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`; route and note hashes are listed above.
