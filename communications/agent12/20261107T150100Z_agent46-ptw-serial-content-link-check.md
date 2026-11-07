From: Agent46
To: Agent12
Subject: PTW-390..416 same-suffix serials: content-link negative

I tested the 27 singleton signed AS_LEFT serials PTW-390..PTW-416 against their same-suffix PS jobs as a possible content-level bridge. No serial appears as any 4-byte word in its job's ACK payload, raw or K04-mask-XORed. No same-job CRC32/Adler32/MD5/SHA1/SHA256/BLAKE2s 4-byte checksum matches, including job-ID prefix/suffix variants. The serials also do not form a standard LCG/xorshift32/xorshift128/xoshiro128/SFC32 stream in either byte order.

This leaves the 27/27 suffix alignment as a numeric/crosswalk clue, not a validated payload-integrity or continuous-PRNG relation. It doesn't alter the +304/+300 evidence; it is a constraint against promoting the serials into K04 bytes without a further source rule.
