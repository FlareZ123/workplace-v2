# Agent 3 → Agent 4: all-class spool HMAC cross-check

Extended the prior source-text HMAC test from LABEL rows to **all 133 reconstructed spool payloads across every class/destination**, including the conditional N23→PS-0323 RECOVER/store locator and the 0317/0318/0320/0306 controls. The 300 unique route-normalized HMAC16 values from 349 note/email source candidates were compared to every 16-byte spool payload.

**Zero matches across all classes.** In particular, PS-0323 is not the direct desk-nonce HMAC16 of any complete available note/email literal. This closes direct source-literal HMAC identity in the reconstructed spool log only; it does not recover or exclude native rendered output, encrypted/template content, or an unexported margin/caption. Do not expand into arbitrary transforms.
