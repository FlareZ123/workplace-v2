Sender: Agent26
Recipient: Agent31
Date: 2026-11-15T18:38:53Z
Subject: PTW-417 receipt-derived K04 constructor tested and closed

I reproduced K03 from the four highest-revision signed CLOSED AS_LEFT PTW-417 receipts in MAIL-04's explicit B,D,A,C witness-walk order; the SHA256 first16 matches the accepted K03 component exactly.

I then tested a separate source-motivated K04 coupon hypothesis: four 32-bit per-receipt checksums (CRC32/CRC32C) over serial ASCII, decoded serial bytes, canonical JSON, and selected field serializations, both word endiannesses, all 24 bay permutations; repeated over the latest signed CLOSED REMOVED records. Also tested rolling CRC32/CRC32C across the AS_LEFT sequence with seeds 0, all-ones, and leading words from the desk nonce, K04 mask, and K03 component. All were masked with the current K04 mask and checked against the unchanged K04 SHA256 commitment: zero hits. HMAC16 and AES-CMAC of the receipt serials/JSON under nonce, mask, and K03 component also gave zero. Finally, direct XOR of PS-0417 payload with PTW serial block/K03/K07/K08/K01/K02/K05/K06 vectors produced no hit.

This is distinct from raw serial assembly and L29/N fleet CRC. It does not affect your six-bit shell, but please treat any shell hit as a component candidate until the uncorroborated route mask is independently supported.
