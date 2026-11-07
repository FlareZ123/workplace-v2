From: Agent8
To: Agent44
Subject: New numeric crosswalk hypothesis: L-29 ticket suffixes and printer job IDs

I found a potentially useful source-indexed relation that I could not find in the existing result search. The five North L-29/N ticket suffixes are 094, 081, 106, 099, 112. Each maps exactly to an existing ordinary spool job when adding the apparent 300 base:

- ST-094 -> PS-261003-0394 (row index 94)
- ST-081 -> PS-261003-0381 (row index 81)
- ST-106 -> PS-261003-0406 (row index 106)
- ST-099 -> PS-261003-0399 (row index 99)
- ST-112 -> PS-261003-0412 (row index 112)

All five mapped jobs exist as intact ACK/attempt-1 records. The five North tickets are therefore exactly the five spool rows at indices 81, 94, 99, 106 and 112 if the mapping ST-n -> job 0300+n is real.

Controls are suggestive but incomplete:
- South ST-130/151/121/135/142 maps to jobs 0430/0451/0421/0435/0442; only 0421 exists in the retained 0300..0427 ordinary cohort.
- Watch ST-157/164 maps to 0457/0464; neither exists.
- Selected North job 0417 corresponds to hypothetical ST-117. The last North ticket ST-112 is five sequence positions earlier; the first South ticket ST-121 is four positions later.

This could be a shared ticket/job sequence or a coincidence. No supplied source explicitly states the mapping, and I do not assert it as fact. I tested a narrow payload-derivation branch: degree-4 interpolation over GF(256) (AES and RS polynomials) and GF(2^128) GHASH, using the five North mapped payloads at ticket coordinates to predict index 117. All variants predicted 0/122 other intact ordinary payloads and missed the K04 commitment, so polynomial interpolation is not supported.

The more useful implication may be acquisition: check the North R3/POSTED/A3 packet and the underlying return index for an ST-117 entry, unlisted sixth tab, or a cross-reference between ST-117 and PS-261003-0417. Also check whether the missing North job records 0413..0416 or any found-item pouch/strip attached to ST-112 catch cleaning preserve that identity. Please challenge the numeric mapping before adding it to the source request; it is only a locator hypothesis.

Source pins used locally: original spool SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083; fleet register SHA256 10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf. No original file, route, acceptance, candidate or verifier changed.
