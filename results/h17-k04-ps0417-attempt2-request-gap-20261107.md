# PS-0417: missing attempt-2 REQUESTED row in the retained spool export

**Status:** source-coverage finding; no K04 bytes recovered.

## Finding

The K04 selector identifies the last acknowledged attempt for exact job `PS-261003-0417`. The retained spool export contains the attempt-2 RECOVER ACK at 18:02 UTC, but it contains **no REQUESTED row for attempt 2**. Its only RECOVER request rows are attempt 1 at 18:01 and attempt 3 at 18:03.

| Spool line | Time UTC | Attempt | State | Class | Payload |
|---:|---|---:|---|---|---|
| 119 | 16:45 | 1 | ACK | LABEL | `E1E60D5F6B6DD2225FA6D5A2A63AD932` |
| 130 | 18:01 | 1 | REQUESTED | RECOVER | `CD3E4F216ADB2FB180DA2AA90B33F7A4` |
| 131 | 18:02 | 2 | ACK | RECOVER | `A9A9DC5731A5E2AE879C47215C2559D5` |
| 132 | 18:03 | 3 | REQUESTED | RECOVER | `44D53DFC29D7943A95D89371DA58EC64` |

The source header describes the file as a retained-fragment reconstruction with unverified payload integrity. MAIL-16 supplies the selector interpretation: use the last acknowledged attempt for the exact job; the later REQUESTED entry is a button press that never received an acknowledgement. MAIL-16 also says the ACK field came from the dispatch log and is not a media-integrity flag.

Together, these establish:
- Attempt 2 ACK is the selected last acknowledged attempt.
- Attempt 3 REQUESTED is explicitly unacknowledged and must remain excluded.
- The export does not preserve the attempt-2 REQUESTED row.
- The attempt-1 RECOVER request is not source-confirmed as the request associated with the attempt-2 ACK. Do not pair its payload with ACK2 by assumption.

## Bounded payload check

For completeness, the attempt-1 and attempt-3 REQUESTED payloads were each tested under the recorded K04 XOR mask and the official K04 SHA-256 commitment. Neither candidate matched. This does not make either row eligible: attempt 1 is not established as the selected attempt-2 request, and MAIL-16 excludes attempt 3 as unacknowledged.

The existing [ACK selector integrity audit](h17-ack-selector-integrity-audit.md) already establishes why dispatch selection must be independent of disputed payload bytes. This finding adds a more specific source-coverage gap: the selected ACK2 has no matching attempt-2 request row in the retained export.

## Retrieval consequence

The next K04 request should explicitly name the missing **attempt-2 REQUESTED record** and require its original relationship to the 18:02 ACK2:
- native print-host queue/journal entry for job `PS-261003-0417`, attempt 2;
- original `.SPL`/`.SHD` data and driver-level job image;
- PrintService/dispatch event records showing request, ACK, retries, copy stage and job identifier;
- the device-side saved job or original printed coupon, with custody and media-integrity evidence.

The original supplier commissioning note should clarify whether the payload to reduce is the attempt-2 request body, the ACK echo, or a separate device-side object. Until that is authenticated, the 18:02 ACK2 remains the selector witness, while its copied 16-byte payload remains unverified.

## Limits

This does not change the last-ACK selector, establish a different attempt, or recover K04. It identifies a specific missing native record needed to bridge the selected dispatch ACK to the actual printed media. No request/ACK pairing should be invented from timestamps alone.
