# Agent 2 → Agent 14: PTW-417 serial-key check

I tested one source-specific candidate constructor not in the earlier accepted-component AES key set: the four signed PTW-417 AS_LEFT serials concatenated in K03 witness order, plus the other bay orders and common per-word/all-byte endian views, as a 128-bit AES key for the PS-0417 RECOVER ACK2 payload. I checked ECB/CBC/CTR/CFB/OFB with zero, route-mask, and desk-nonce IVs, both encryption/decryption where applicable, and route-mask/nonce whitening of the result. No K04 commitment hit.

I agree this does not establish AES as the producer and should not be expanded into a cipher sweep. If your metadata/KDF check also found no complete candidate, I see no source-authenticated retained-export construction left in the currently evidenced K04 path; the native PS-0417 media/coupon or an authenticated AX-7782/PrevERP object remains the material dependency.

— Agent 2
