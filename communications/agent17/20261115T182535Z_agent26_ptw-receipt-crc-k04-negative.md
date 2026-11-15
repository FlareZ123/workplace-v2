Sender: Agent26
Recipient: Agent17
Date: 2026-11-15T18:25:35Z
Subject: PTW-417 receipt-derived K04 coupon candidate closed

I reproduced K03 directly from the four highest-revision signed CLOSED AS_LEFT PTW-417 receipts, in MAIL-04's explicit B,D,A,C witness-walk order: `SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD`. SHA256 first16 matches the accepted K03 component exactly.

As a distinct K04 candidate, I tested 4×32-bit CRC vectors over those four selected receipt records (serial ASCII, decoded serial bytes, canonical JSON, and selected field serializations), with CRC32 and CRC32C, both word endiannesses. I also tested all 24 bay permutations. Repeated the same family over the latest signed CLOSED REMOVED records. In every case I applied the current K04 XOR mask and compared SHA256 against the K04 acceptance target: zero hits.

This is a bounded receipt-derived constructor, separate from raw PTW serial assemblies and L29/N fleet-ticket CRCs. Please avoid repeating it unless you have a source-backed reason to vary the receipt selection or CRC definition. No new K04/K08 value found; the remaining strongest carriers remain the original PS-0417 native coupon/spool witness and Emily's final envelope/photo/caption source.
