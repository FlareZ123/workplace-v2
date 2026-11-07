# K08: PS-0324 sequence-mapped label row (envelope attribution withdrawn)

**WITHDRAWN:** The prior claim that PS-0324 is the strongest final-envelope-label target is unsupported.** This correction replaces the prior report's incorrect N24 quotation and authorship attribution. The previous version remains in Git history.

## Source correction

The supplied source `resources/evidence/crew/noticeboard-and-desk-notes.txt` contains one N24:

> N24 / Gabriel [censored]  
> Departure board: Every crossing begins with somebody trying to find their other glove.

N24 is Gabriel's departure-board note. It does not contain the sentence previously attributed to it:

> The page is ready to go back in the folder; the envelope gets the shorter wording, not the whole explanation.

A search of the supplied evidence finds no “page is ready”, “shorter wording”, or “whole explanation” sentence. MAIL-20 also contains no such instruction. No separate original source path or line for the quotation has been identified.

Therefore, the prior report's claims that N24 is Emily's final numbered desk note, that N24 explicitly describes the shorter envelope wording, and that PS-0324 is the strongest final-label target are withdrawn.

## What remains supported

The independent [N01–N24 / PS-0301–0324 sequence crosswalk](h17-k08-note-spool-sequence-crosswalk-20261107.md) establishes a structural pattern:

- N01–N24 each have one same-suffix PS-0301–0324 row.
- Every corresponding row is ATTEMPT=1 / ACK.
- The timestamps advance in exact five-minute steps from 07:05 to 09:00 UTC.
- N24 is Gabriel's departure-board note and aligns by sequence with PS-0324, a LABEL/store row.
- N23 is Emily's envelope/margin note and aligns by sequence with PS-0323, a RECOVER/store row.

The sequence is not an authenticated causal job-to-document join. It does not prove that PS-0324 printed an envelope label or that PS-0323 rendered Emily's final words.

The relevant K08 source context remains:

- **N20 / Emily:** her semantic brief asks for a line holding the sea, the end of the night and voices at the table, and says not to reuse the shorter standby label.
- **N23 / Emily:** “The wording in my margin was never an official slogan. The envelope only remembers the words I finally put on it.”
- **MAIL-11 / Emily:** the final desk phrase is neither the standby label nor the commissioning label; the desk notes and photograph captions informed the wording.
- **MAIL-20 / Gabriel:** Emily's description concerned the late crew making room for one another; several captions and drafts were on her desk; the exact words she finally chose matter.

These sources identify the missing evidence as Emily's original final wording, margin, envelope/card or photograph/galley-caption material. They do not identify a final print job.

## Retained PS-0324 packet facts

The retained spool row is:

`2026-10-03T09:00:00+00:00 JOB=PS-261003-0324 ATTEMPT=1 STATE=ACK CLASS=LABEL PAYLOAD=A2F9F16F4E3C05F1C19C70455EF8D876 DEST=store`

This establishes only that the reconstruction contains a PS-0324 ACK row with those fields. The log warns that payload integrity is unverified; ACK is not proof of rendering, physical collection, or envelope attachment.

The prior version recorded that the decoded PS-0324 payload's direct SHA-256 did not match K08, that a direct scan of 133 retained payloads found no K08 commitment hit, and that 31 nonempty XOR subsets of PS-0300, PS-0317, PS-0318, PS-0323 and PS-0324 found no hit. Those bounded packet checks do not establish the identity of the printed item and do not recover the phrase. They do not test rendered text, native document bytes, driver transformations or physical output.

## Corrected retrieval priority

1. **Original K08 wording source:** Emily's WN-14 margin, original envelope/card, desk notebook, Bundle 06 manifest/trim log, and separate photograph/galley-caption originals. Preserve physical order and custody.
2. **Native note/job evidence:** PS-0323 and PS-0324 original job objects and rendered outputs may be useful witnesses because of the sequence association. PS-0323 is text-adjacent to N23; PS-0324 is sequence-associated with Gabriel's departure-board note. Neither is established as the final envelope output.
3. **Controls:** PS-0317 and PS-0318 remain the standby and commissioning label controls; PS-0320 is the N20 semantic-brief sequence row; PS-0306 is the N06 draft sequence row. PS-0300 remains an unassigned prelude.
4. **Causal join:** the original queue/job manifest, native source-document references, rendered-output records, physical collection/eject evidence and custody records are required before any PS job can be called the envelope label.

MAIL-16 assigns ESC-N to K04, calls WATCH-SPARE unrelated, and excludes ESC-S from the keeper's desk phrase. The supplied route mapping covers PS-0417, PS-0420 and PS-0448; it does not establish a route for PS-0323 or PS-0324. Do not infer that either job used an H-17 recovery queue or that its output was collected.

## Decision

PS-0324 is retained only as a **sequence-mapped LABEL/store row**. Its final-envelope attribution and priority are withdrawn. PS-0323 remains a conditional, text-adjacent retrieval lead, not an authenticated output. No exact phrase or K08 component has been recovered.
