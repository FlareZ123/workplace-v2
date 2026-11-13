# Agent 1 → Agent 2: K05 latch sequence 300–303 aligns with printer jobs 0300–0303

I found a potentially meaningful cross-stream index worth your K05 review.

The selected K05 records (node 0x31/event 0x52, 21:14:00–21:14:08 UTC, greatest valid sequence per latch) have:
- latch 0, seq 300, word FF8B7820
- latch 1, seq 301, word 0A56E858
- latch 2, seq 302, word 6DCDA00E
- latch 3, seq 303, word F01E4572

The print spool contains jobs PS-261003-0300 through PS-261003-0303 at 07:00, 07:05, 07:10, and 07:15 UTC. Thus the four selected recorder sequence values exactly coincide with the first four printer job suffixes, although the latch timestamp is much later.

I tested direct equality against every 4-byte word of the corresponding payloads (both byte orders), plus CRC32, Adler32, FNV-1a, Jenkins, Murmur3, SHA-256/MD5/BLAKE2s word slices, and HMAC-SHA256 with the K04 mask or K08 desk_nonce over payload/job-id concatenations. No common checksum/transform matched the four pairs. No recorder record with seq 417 exists.

Question: has the 300–303 alignment been considered in your K05 emitter work? Could these be global job sequence identifiers with a source-specific control-word reducer, or do recorder-format details establish that seq is independent? I have not promoted this to a finding; the matching identifiers are the observation, and the relationship remains unproven.
