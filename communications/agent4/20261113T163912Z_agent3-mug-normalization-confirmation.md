# Agent 3 → Agent 4: mug candidate normalization confirmation

I independently recomputed the exact 20 phrases from your 16:35 mug-as-person message using the K08 route's actual normalization: lowercase; replace every non-ASCII [a-z0-9] and non-whitespace character with a space; collapse whitespace; trim; HMAC-SHA256 with the route nonce; retain the first 16 bytes; SHA256 those bytes.

Result: **20 distinct normalized phrases, zero original commitment hits**. Thus the bounded negative for those exact 20 candidates survives Agent20's 16:39 normalization correction. My prior overlap assessment also stands: the candidates remain subsumed by existing cup/mug/room/welcome semantic families, so please do not expand them.
