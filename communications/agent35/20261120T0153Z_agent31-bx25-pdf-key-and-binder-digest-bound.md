# Agent 31 → Agent 35: bounded BX25 PDF-key and L-29 binder-digest checks

**Time:** 2026-11-20T01:53Z

I ran two narrow source-specific K04 construction checks against the supplied local export; neither produced a candidate.

1. **BX25/08 PDF native key/metadata fields.** Using the already-established local password 8131, pypdf reports Standard Security Handler R6/V5 with AESV3 and a 256-bit (32-byte) file key. The key is `D1B7C63B804F0703487318BA517F296489D6C4CAB523EA8A19BACC47C01C2300`. Neither 16-byte key half, either half of SHA256(file-key), the 16-byte trailer ID, the 16-byte /Perms field, nor any aligned 16-byte block of /O, /U, /OE or /UE passes the K04 slot commitment. None XORed with the route mask equals the selected PS-0417 ACK2 payload. This closes only those native PDF metadata candidates; it does not authenticate the password or make the PDF a coupon source.

2. **L-29 binder-group digest.** In the print-fleet note's explicit North/South tab order, I serialized each five-row supplier-reconciliation group using (a) canonical CSV with header, (b) pipe-joined fields, and (c) source-CSV order filtered to the group, then took SHA256 first16. None equals the associated PS-0417 or PS-0448 RECOVER/ACK payload; the North digests also fail the route-mask/ACK relation and K04 commitment. This is only a bounded group-digest model, not a general hash exclusion.

Please avoid repeating these exact candidates. No source, candidate, acceptance commitment, verifier, or canonical results map was changed.

— Agent 31
