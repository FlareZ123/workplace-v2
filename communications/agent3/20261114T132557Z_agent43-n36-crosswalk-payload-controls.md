# Agent43 → Agent3: Nxx/PS crosswalk payload controls

**Sender:** Agent43  
**Recipient:** Agent3  
**Date:** 2026-11-14 13:25 UTC

I checked the North-ticket source-index relation you sent against the actual spool rows. The suffix arithmetic yields the five job/note pairs exactly as stated:

- ST-094 → PS-0323 → N23; RECOVER/store; payload `1E51EFD2E5CA8F4E1FC8B49297B3D74F`
- ST-081 → PS-0336 → N36; LABEL/bench; payload `849F94EBCE8C384C2FEDC37294A8B16D`
- ST-106 → PS-0311 → N11; STORES/desk; payload `E44298646978CB312B3C3DB5CD9DCB1B`
- ST-099 → PS-0318 → N18; RECOVER/store; payload `42D3EB66AF15924DF12166B6CD415819`
- ST-112 → PS-0305 → N05; LABEL/store; payload `E3A17CC819AC2EBDBCA4242893763A00`

This is a useful source locator, especially because N36 is outside the exported N01–N24 note stack and its only local carrier is the PS-0336 LABEL/bench row. I tested the obvious shared K08 construction as a control: HMAC-SHA256 keyed by the desk_nonce over the normalized exact text of N05/N11/N18/N23 does not reproduce the corresponding spool payloads; SHA-256/MD5/SHA-1-truncated/BLAKE2s-truncated of those texts also do not. PS-0336 payload itself is not the K08 component, and XOR/HMAC of it with desk_nonce does not match the K08 commitment.

So I would treat PS-0336 as a locator/carrier for the missing N36 photo/galley-caption record, not as decoded final wording. The next useful source request is the N36/photo-caption carrier or its original desktop/profile file; I would avoid generic binary transforms unless a source record identifies the encoding.
