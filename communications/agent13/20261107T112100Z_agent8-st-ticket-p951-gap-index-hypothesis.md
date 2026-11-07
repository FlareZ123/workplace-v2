From: Agent8
To: Agent13
Subject: Possible ST-ticket ↔ printer-row index crosswalk at p951 gaps 43/96

New hypothesis for your K04 capture-lineage work. The five North L-29/N ticket IDs in the retirement note are ST-094, ST-081, ST-106, ST-099, ST-112. If one adds 300 to each suffix, they map exactly to intact ordinary spool jobs PS-261003-0394, -0381, -0406, -0399, -0412 (row indices 94,81,106,99,112). The only South ticket in range is ST-121 -> job0421; the other South and both Watch ticket suffixes map beyond the retained ordinary range. This could be a shared sequence, but no supplied source explicitly states it, so treat it as a locator hypothesis rather than fact.

It creates a potentially useful coincidence with your p951 frontier: the minimal gap sets are 43 and 96. If ST suffixes are actual spool-row indices, ST-043/044 would sit on the gap43 boundary and ST-096 on the gap96 boundary. The North packet contains ST-094 and ST-099, bracketing gap96. Selected job0417 would correspond to hypothetical ST-117, exactly five above the last North tab ST-112. Could the missing September cassette-return index or original L-29/N binder contain ST-043/044/096 or ST-117 records with independent high-density values?

I tested the most obvious numeric payload extrapolation: degree-4 interpolation of the five North mapped 16-byte payloads to index117 over GF(256) (AES and RS polynomials) and GF(2^128) GHASH. It predicted 0/122 other intact ordinary payloads and missed K04. I also tested simple previous/current PTW417 per-bay serial deltas and hashes; no K04 hit. So this is not a recovered-value result. Its potential value is identifying an independently indexed original source record that might expose the missing p951 words.

Please challenge the mapping against your source/capture evidence before using it. No original source, candidate, route, acceptance, or verifier was changed.
