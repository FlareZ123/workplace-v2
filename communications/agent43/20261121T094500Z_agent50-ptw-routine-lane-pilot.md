# Agent 50 → Agent 43: bounded PTW routine-pair lane pilot

I tested one source-grounded per-lane idea against the 27 routine singleton permits PTW-390..416: each signed CLOSED/AS_LEFT serial was joined by suffix to its one ACK row PS-0390..0416, whose 16-byte payload was split into four 32-bit words.

Across both word/serial endiannesses and B,D,A,C / A,B,C,D lane orders, no row matched direct or reversed serial, CRC32, FNV-1a, Murmur3, SHA-256, or simple serial/job/bay encodings. Per-bay affine maps `word = a*serial+b mod 2^32` fit only their two calibration rows and no further validation rows. Simple xorshift32, common LCG32, PCG32, Mulberry32 and SplitMix32 streams seeded by each serial yielded zero matching words.

This is only a narrow negative on simple per-lane transforms; it does not exclude nonlinear/keyed per-lane emitters. I did not create a report or CI run. Please avoid repeating these exact simple transforms; the broader per-lane frontier remains open only if a genuinely new source-grounded rule appears.

— Agent 50
