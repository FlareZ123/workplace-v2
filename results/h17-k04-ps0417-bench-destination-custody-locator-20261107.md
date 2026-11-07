# K04: PS-0417 DEST=bench as a physical-custody locator

**Status:** new acquisition lead; destination semantics unresolved; no K04 bytes recovered.

## Source observation

All four retained PS-261003-0417 rows carry `DEST=bench`:
- line 119: attempt 1 ACK/LABEL;
- line 130: attempt 1 REQUESTED/RECOVER;
- line 131: attempt 2 ACK/RECOVER, the last acknowledged attempt selected by MAIL-16;
- line 132: attempt 3 REQUESTED/RECOVER.

The selected K04 route is ESC-N, and its selected ACK2 record is addressed to `bench`. The route file does not define the physical meaning of the spool `DEST` field. The local custodian and mail notes identify the recovery envelope and the ordinary records-folder handoff, but they do not establish that the K04 printer output was delivered to or stored inside that envelope.

## Consequence

Keep the K04 physical coupon and the K08 keeper's-desk phrase as separate carriers until custody evidence joins them. Ask the custodian to resolve `DEST=bench` against the original print-host queue/port configuration and the physical workflow:
- Was `bench` a printer queue, a physical bench/output tray, a collection point, or a later handoff destination?
- Where were ESC-N outputs collected after ACK, and who cleared or signed for them?
- Was there a bench job pocket, output tray, collection bin, print strip, or return envelope for PS-0417?
- Is there a bench-to-desk or bench-to-ordinary-records-folder transfer record for the 18:02 ACK2 output?
- Were the later attempt-3 request and its unacknowledged state recorded at the same destination?

Preserve the original queue/port mapping, output-location labels, job ticket, handoff record and any physical media together. Photograph the arrangement before separating loose items.

## Limits

`DEST=bench` is a direct spool-log field. Its physical meaning is not established by the surviving local export. This result does not assert that a physical bench existed, that the coupon is there, or that the envelope and coupon were separate. It identifies a destination mapping and custody join that the current acquisition request should resolve.

This locator supplements the specific attempt-2 REQUESTED-row gap in [the PS-0417 attempt-ledger finding](h17-k04-ps0417-attempt2-request-gap-20261107.md).
