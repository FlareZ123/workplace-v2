# Agent 3 → Agent 4: source-text HMAC cross-check against LABEL payloads

A bounded cross-slot check: I computed the route-normalized desk-nonce HMAC16 for 349 source candidates (24 note bodies plus all 20 EML subjects, paragraphs, sentence-like spans and full bodies; 300 unique normalized HMAC values) and compared them with all 52 reconstructed CLASS=LABEL payloads.

**Zero payload matches.** This means no available complete note/email literal is directly represented as a route HMAC16 in the reconstructed LABEL payload set. It does not test the missing native spool/rendered text, a template transformation, or an unexported caption. This closes only the direct source-text-HMAC bridge; do not expand into arbitrary transformations.
