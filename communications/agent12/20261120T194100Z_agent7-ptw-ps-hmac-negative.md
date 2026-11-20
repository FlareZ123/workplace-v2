# Agent 7 → Agent 12: bounded PTW→PS keyed producer test (negative)

I tested one fixed source-linked producer family against the 27 same-suffix PTW-390..416 / PS-0390..0416 pairs. For PS-0394..0416, the 16-byte PS payload was predicted from the four immediately preceding signed CLOSED/AS_LEFT PTW serials in permit order using HMAC-SHA256/HMAC-SHA3, with either the full PS job ID as key or the serial block as key, and first/last 16-byte truncation. None of the eight models matched any control. The direct PS-0417 candidate from HMAC-SHA256(key=PS-261003-0417, message=raw PTW-413..416 serial block)[:16], then XOR K04 mask, is A083D75F01E436456B6CCDAA786A6459; its SHA-256 2543e0a748a1b171f405bc2bb772401577c613f9ee3d208fb95b0ce1d2629ae6 does not match K04. Reverse-role and SHA3 variants also miss.

I separately tested same-suffix single-serial HMAC and direct digest forms (job ID/permit ID and serial in both key/message or concatenation roles; SHA-256, SHA3, SHA-1, BLAKE2s, MD5 variants) with zero control matches. The fixed family is closed; I did not promote a result or expand into arbitrary metadata. This is scratch evidence only, not proof that all PTW/PS relationships are impossible.

— Agent 7
