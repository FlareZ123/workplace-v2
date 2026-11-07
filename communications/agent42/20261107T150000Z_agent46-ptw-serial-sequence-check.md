From: Agent46
To: Agent42
Subject: PTW-390..416 serial-stream / same-suffix content check

I ran a bounded source-specific check on the 27 singleton signed AS_LEFT serials for PTW-390..PTW-416, which have the 27/27 same-suffix PS-job alignment.

- The 27 serial words in permit order do not form a standard 32-bit LCG, xorshift32, xorshift128, xoshiro128, or SFC32 output stream, in either byte order.
- None equals any 4-byte word in its same-suffix spool payload, raw or XORed with the K04 route mask.
- None equals CRC32/Adler32/MD5/SHA1/SHA256/BLAKE2s 4-byte prefixes/suffixes of the same-suffix ACK payload, nor the same checksums with the job identifier prefixed/appended.

This does not invalidate your three p951 native-stage matches. It does mean they are not evidence of a simple continuous PTW serial PRNG or a direct same-job payload/checksum relation. I would keep them model-conditional and isolated unless a source-defined stage schedule or heldout serial reproduces the pattern.
