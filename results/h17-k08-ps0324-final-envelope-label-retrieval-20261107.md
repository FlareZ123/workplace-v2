# K08: PS-261003-0324 as the final short-envelope-label retrieval target

**Status:** strong, source-grounded print-output locator; no final wording or K08 component recovered.

## Question

Which preserved print job is most likely to contain the *short wording actually placed on the recovery envelope*?

## Source basis

N24 is Emily's final numbered desk note:

> The page is ready to go back in the folder; the envelope gets the shorter wording, not the whole explanation.

The preserved note-to-spool sequence associates N01–N24 with PS-261003-0301 through PS-261003-0324 at exact five-minute intervals. Under that conditional sequence join:

- **PS-0323, 08:55Z:** N23, `CLASS=RECOVER`, `DEST=store`. N23 says the last line should be shorter than the first draft and that the envelope remembers the words put on it.
- **PS-0324, 09:00Z:** N24, `CLASS=LABEL`, `DEST=store`. N24 explicitly says the envelope gets the shorter wording.

The K08 route defines the missing component as the HMAC16 of the keeper's final desk/envelope phrase, used to distinguish the recovery envelope from the commissioning and standby envelopes. N17/PS-0317 and N18/PS-0318 are the preserved standby/commissioning label controls. On the available evidence, **PS-0324 is the strongest candidate for the final rendered envelope label**, with PS-0323 as its immediately preceding wording/draft source. PS-0300 remains a separate orphan prelude locator.

## Bounded packet checks

PS-0324's retained spool row is:

`2026-10-03T09:00:00+00:00 JOB=PS-261003-0324 ATTEMPT=1 STATE=ACK CLASS=LABEL PAYLOAD=A2F9F16F4E3C05F1C19C70455EF8D876 DEST=store`

SHA-256 of its decoded 16-byte payload does not match the K08 commitment. A wider direct carrier test over all 133 retained decoded payloads also found zero matches.

I additionally tested every nonempty XOR subset of the five source-located jobs PS-0300, PS-0317, PS-0318, PS-0323 and PS-0324: **31 combinations, zero K08 commitment hits**. This excludes only direct HMAC16 storage and these bounded raw-payload XOR combinations. It says nothing about rendered text, native document bytes, driver transformations, or physical output.

## Retrieval request

If an authorized historical profile-refresh package, workstation image or native spool backup becomes available, prioritize:

1. **PS-261003-0324** original `.SPL/.SHD` or equivalent native job object, rendered/printed output, source document bytes, job/queue/host/device/port mapping, driver/print-processor context, dispatch and completion records, media-eject/collection receipt, and custody.
2. **PS-261003-0323** with the same metadata as the immediately preceding N23 wording/draft source.
3. **PS-261003-0317** and **PS-261003-0318** as the standby and commissioning envelope controls; preserve **PS-261003-0300** as the unassigned prelude candidate.
4. The original queue/job manifest or other independent record that authenticates the N01–N24 ↔ PS-0301–0324 association and identifies which output was actually attached to the recovery envelope.
5. The original WN-14 margin, envelope/card itself, and separate photograph/galley-caption originals. A printed label does not replace Emily's handwritten final source if the HMAC input was transcribed from that margin.

## Limitations and decision

- The N24↔PS-0324 mapping is supported by exact suffix/time sequence but remains a structural association, not an authenticated causal job-to-document join.
- `LABEL / DEST=store` is not unique; 17 jobs share the class/destination pair.
- The retained ACK is dispatch evidence, not proof of rendered-media integrity or collection.
- The packet payload is opaque and is not the K08 HMAC16.
- No queue mapping for PS-0324 or physical envelope receipt is present in the supplied export.

**Decision:** promote PS-0324 to the highest-priority conditional K08 rendered-envelope retrieval target; retain PS-0323 as the adjacent draft/source job and PS-0300 as an earlier prelude. Do not claim that any of them contains the final phrase until the native output and custody join are recovered. No candidate wording was generated or promoted.
