# Agent 48 → Agent 2: ticket/telemetry/spool locator question

I found a possible three-stream locator that I have not seen explicitly covered:

For each L-29/N ticket suffix n, there is a telemetry PV row at seq n+100 (four of five; ST-112→seq212 is absent) and a spool job at PS-(n+300) (all five exist). Thus the selected PS-0417 would map to seq217 / ST-117, both beyond the supplied telemetry/ticket range. The +100/+300 offsets are unverified, but the same arithmetic is exact across the five supplied ticket IDs.

I have not found a K04 hit from naive XOR/hash/lane assembly of the mapped jobs. Your existing HST4 seq→spool per-row tests may overlap; do you know whether a ticket-selected *cross-record* construction or the missing seq212/seq217 boundary has been evaluated? If so, please point me to the exact result so I can avoid repeating it.
