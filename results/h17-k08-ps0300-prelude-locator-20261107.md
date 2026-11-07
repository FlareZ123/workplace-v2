# K08 PS-0300 orphan prelude locator (7 November 2026)

## Observation

The supplied spool reconstruction contains a 24-job sequence from PS-0301 through PS-0324. Those jobs align one-to-one with N01 through N24 at five-minute intervals. PS-0300 is an additional job immediately before that sequence:

| Job | Displayed UTC time | Class | Destination | Note relationship |
| --- | --- | --- | --- | --- |
| PS-0300 | 07:00 | LABEL | store | Orphan prelude; no N00 entry |
| PS-0301 | 07:05 | STORES | bench | N01 |
| PS-0317 | 08:25 | LABEL | store | N17, standby envelope label |
| PS-0318 | 08:30 | RECOVER | store | N18, commissioning envelope label |
| PS-0323 | 08:55 | RECOVER | store | N23, final-margin note |
| PS-0324 | 09:00 | LABEL | store | N24 |

PS-0300 is exactly 300 seconds before the first note-aligned job. Its position makes it a useful prelude locator for the K08 desk/envelope material. The LABEL/store class-destination pair occurs on 17 jobs in the full spool reconstruction, so those fields do not uniquely identify its printed content.

## Bounded local screens

The PS-0300 payload is `FBBBC54356483F5864BB3F06794518A5` in the supplied spool reconstruction. It was compared against seven common 16-byte digest/HMAC outputs for 111,586 distinct normalized contiguous spans from the 20 EML subjects/bodies plus N01-N24. No match appeared. The seven tested outputs were MD5, SHA-1 first 16 bytes, SHA-256 first 16 bytes, SHA-256 last 16 bytes, BLAKE2s-16, HMAC-SHA256 first 16 bytes with the declared desk nonce, and HMAC-SHA256 first 16 bytes with the K04 mask.

A separate K08 acceptance-HMAC screen over 4,871 normalized contiguous spans from N01-N24 and the seven-entry galley/stores log also produced zero hits. These screens leave the printed output itself outside the surviving text export.

## Chronology and limits

The displayed mail dates place MAIL-12's shelf-card note on 2 October at 06:33Z, PS-0300 on 3 October at 07:00Z, and MAIL-20's preservation-bundle message on 4 October at 11:06Z. The original mail-store send times remain unauthenticated. This sequence allows PS-0300 to be considered as a later label or folder prelude. It does not establish that the job contains the final K08 wording or that it relates to the shelf card.

## Next evidence

If an authorized profile image or native spooler source already exists, preserve the native PS-0300 job record, dispatch and receipt records, queue/driver metadata, and rendered output. Compare those records with PS-0317, PS-0318, PS-0323, and other LABEL/store controls. Keep the rendered output and custody evidence together. Do not infer text from the 16-byte payload or launch a broader search based only on class and destination.

No K08 candidate was recovered or promoted.
