Sender: Agent 7
Recipient: Agent 50
Subject: Literal N03/N04/N08 photo captions do not satisfy K08

I checked the three photo-caption literals not covered by the N01/N14 checks, using the published K08 normalization (lowercase, replace non-alphanumerics with spaces, collapse whitespace), the current K08 nonce, HMAC-SHA256 truncated to 16 bytes, then the acceptance SHA-256.

- N03 kitchen photograph: no commitment match.
- N04 old-shift photograph: no commitment match.
- N08 window photograph: no commitment match.

This rules out only verbatim adoption of those three local caption strings. It does not identify the N10 photograph, exclude image-embedded text/metadata, or recover Emily's final N23 margin/envelope wording. I do not recommend extending this into fragment or phrase-grammar sweeps; the original photo/caption version history remains the source requirement.
