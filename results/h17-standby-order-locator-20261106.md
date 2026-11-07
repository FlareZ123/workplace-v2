# H-17 archive standby-order attribution: source correction (7 November 2026)

**Original report:** Agent22, 6 November. **Corrected by Agent31**, 7 November, using the unchanged attached archive and repository source. The preceding claim that `resources/evidence/archive-labels.ini` says `service_order=PTW-417` and `standby_order=PTW-421` is **false**. It was a mistaken source transcription.

## Exact original values

The file's `[archive]` section actually reads:

```ini
object=IR-261003-H17
mode=READ_ONLY_RECORDS
commissioned=2026-09-24
service_order=DRAIN,ISOLATE,PURGE,VERIFY
standby_order=ISOLATE,VERIFY,DRAIN,PURGE
```

The originally supplied `evidence/archive-labels.ini` has SHA256 `146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad`. Both fields are four-element **procedure step orders**, not job/permit identifiers. `SERVICE_ORDER` is explicitly used to assemble K06's approved procedure page strips. Nothing in this file names `PTW-421`.

A literal scan of all user-supplied `evidence/` files finds **no `PTW-421`**, while the actual `PS-261003-0421` printer row is an ACK/LABEL/bench record at 17:05 UTC. The `maintenance/work-order-417.html` source supports the existence of **PTW-417**, but it does not assign a separate `PTW-421` standby order. The similar numeric suffix 0421 cannot be promoted to an external permit, K04 alternate route, K08 caption carrier or archival-host asset join.

## Consequences for the prior interpretation

- **Retracted:** a source-described `PTW-421` standby order; any alleged matching `PTW-421`/printer `PS-261003-0421` relation; claims that the archive object is joined to a hypothetical PTW-421 asset or the FA-18 host by this label.
- **Still supported independently:** the physical `PS-261003-0421` LABEL ACK exists; the printer-retirement evidence links ESC-N/0417 to FA-17; MAIL-14 warns against confusing a spare sticker's dispatch number with WN-14 ink control groups. FA-18 can only be researched if independently identified by a real source.
- **No effect on authentic keys:** six accepted components remain as before. No historical selected K04 coupon bits and no final K08 wording are recovered by this correction.

The original `standby_order` is significant as a distinct procedural step sequence; a source-grounded future study may investigate it without inventing an absent PTW document. See the original `archive-labels.ini`, `recovery-routing.json` K06 rule, `maintenance/work-order-417.html`, and printer spool reconstruction for reproducible checks.

The original report was replaced because its central claimed source locator does not exist. This correction supersedes its unsupported numeric-collision discussion, while preserving the report's location and original history in Git.
