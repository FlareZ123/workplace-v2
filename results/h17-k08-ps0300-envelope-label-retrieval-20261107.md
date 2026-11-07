# K08: PS-261003-0300 as a conditional recovery-envelope label locator

**Status:** new source-retrieval hypothesis; no K08 words or component recovered.

## Question

Could the unassigned PS-261003-0300 print job preserve the recovery-envelope label or its rendered text, including Emily's final keeper phrase?

## Source basis

The accepted K08 route in `resources/evidence/recovery-routing.json` defines the component as the HMAC16 of the keeper's desk phrase, normalized with the recorded desk nonce. The route describes a personal caption used to distinguish the recovery envelope from similarly named commissioning and standby envelopes. Crew notes N17 and N18 explicitly identify those two other labels; their note/spool alignment places them at PS-261003-0317 and PS-261003-0318.

The preserved spool reconstruction has an unassigned **PS-261003-0300** row at 07:00Z on 3 October: `STATE=ACK`, `CLASS=LABEL`, `DEST=store`, payload `FBBBC54356483F5864BB3F06794518A5`. The N01–N24 note/spool sequence begins at PS-0301, so PS-0300 is the immediately preceding label job and has no note-body mapping. This makes it a plausible cover/envelope-label job to retrieve before expanding phrase-generation work.

The same job could conceivably have been a shelf card. MAIL-12 says a small card was placed by the mug shelf, but it does not identify a print job. PS-0300 is about 24 hours and 27 minutes after MAIL-12, so that interpretation is weaker and remains unproved. The K08 route's recovery-envelope distinction is the stronger reason to retain PS-0300 as a locator.

## Bounded test

I decoded the 16-byte `PAYLOAD` field from all **133** retained spool rows and compared SHA-256 of each decoded payload with the immutable K08 slot commitment (which commits to the HMAC16 output). **No row matched.** PS-0300's decoded payload hashes to `3dacaee9b03749294ecb8b9b371e3ffaa219eb3704bab60bf9988308b4113717`, not the K08 commitment.

This excludes literal storage of the K08 HMAC16 in any retained packet payload. It does **not** test native spool document content, rendered label text, or a separately stored output image. The spool reconstruction records opaque payload bytes and dispatch ACK state; it is not the native rendered document or a media-integrity witness.

## Retrieval request

If an already-authorized historical workstation image, profile-refresh store, or native spool backup becomes available, preserve for PS-261003-0300:

1. Original `.SPL/.SHD` files or equivalent native job object, unmodified, with hashes and acquisition metadata.
2. The rendered label/output, print processor and driver context, queue/port/destination mapping, and job-to-envelope or job-to-card index.
3. Dispatch, collection, and physical filing records, plus any preserved scan/photograph of the corresponding recovery envelope or shelf card.
4. The original PS-0417 attempt-2 job material in the same acquisition, because K04 and K08 may share the historical workstation/spooler source channel.

A native label that actually contains the final words still needs independent linkage to the H-17 recovery envelope and Emily's final choice. If PS-0300 is unrelated, the job-to-envelope index should establish that too. A handwritten final margin remains a separate K08 witness; PS-0300 is not a substitute for it.

## Limitations and decision

- `LABEL / DEST=store` is not unique; there are 17 such jobs in the retained spool.
- No supplied source joins PS-0300 to the recovery envelope, Emily, or the shelf card.
- The job's 16-byte payload is opaque and fails the direct K08-HMAC16 carrier check.
- MAIL-20/N23 still leave open that the final phrase was handwritten after the print job.
- No candidate wording was generated or promoted.

**Decision:** retain PS-0300 as a conditional, high-value native-output retrieval target alongside PS-0417. Do not claim it contains the phrase. Current recovery remains six accepted components, K04 and K08 missing, combined key incomplete.
