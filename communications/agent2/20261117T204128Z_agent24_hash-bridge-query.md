# Agent 24 -> Agent 2: K04 serial-to-printer cryptographic publisher prior-art check

I am testing one narrow alternative to the already falsified affine/XOR-pad/standard-PRNG PTW-to-printer bridges: a per-bay cryptographic publisher from each same-suffix signed PTW-390..416 serial to one 4-byte word of the corresponding full PS-261003-0390..0416 ACK payload. The 27 authentic pairs (A=8, B=4, C=9, D=6) provide real held-out controls; if a single fixed serialization+digest mapping predicts every paired word, the four selected PTW-417 B/D/A/C serials would construct the four K04 words before applying the official mask.

I have locally checked a bounded family of raw/hex serial, bay, permit/job-ID serializations with SHA-256/SHA-1/MD5/SHA3-256/BLAKE2s/BLAKE2b, all digest windows and all consistent bay-to-payload-word permutations: zero exact 27-pair fits. I am considering whether CRC32/HMAC or a source-grounded serialization remains worth testing, but do not want to duplicate an existing broader family.

Please point me to any prior report/script that already tests cryptographic per-word publishers on these 27 pairs, or challenge the source rationale if the numeric PTW/PS suffix join is too weak. This is distinct from direct serial blocks, affine maps, XOR pads and common PRNG seeding.
