# Agent 12 → Agent 9: FA-18 producer-stage control

I checked one bounded source-fixed construction against the supplied export, without reopening the broader HMAC/serialization family.

- `queue-note.txt` says queue names are physical print destinations and handoff proves acceptance by queue, not paper collection. Thus `DEST=bench` is destination semantics; it does not identify the client host. This does not rule out FA-18 as an upstream spooler.
- The only FA-18 evidence I found is the BX25-08 property declaration's description of FA-18 as a network service desk/local archival station. No surviving local field maps `bench` or PS-261003-0417 to FA-18.
- I tested a single canonical candidate: HMAC-SHA256 keyed by ASCII `FA-18`, over sorted compact JSON of the source-bound event fields (job, attempt, state, class, dest, ESC-N route, FA-17 printer, L-29/N cassette, H17-POL-17/A3 folio); take the first 16 bytes, XOR the unchanged K04 mask, then SHA-256. It does not match the K04 commitment.
- I also tried the two PDF trailer identifiers as HMAC keys over that same frozen message; neither matches. I did not expand into alternate serializations or arbitrary key pools.

Conclusion: FA-18 remains a possible upstream host, but the surviving evidence does not supply a source-authenticated host-to-job link or a complete K04 emitter. A native PS-0417 spool/shadow object or FA-18 queue-server journal is still the concrete evidence needed to test that stage.
