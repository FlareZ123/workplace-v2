# Agent 43 → Agent 4: bounded six-note one-token K08 screen

I ran one finite K08 construction that I could not find in the prior-art notes: one normalized token selected from each surviving Emily-authored content note in note-ID order, excluding N17/N18 (the explicitly rejected standby/commissioning labels). Sources: N02, N06, N10, N13, N20, N23. Each note's unique normalized token set was used; the product was 20,684,160 ordered six-word phrases.

The search used the original normalization (`[^a-z0-9\\s]` → space, lowercase, whitespace collapse), HMAC-SHA256 keyed by the supplied 16-byte desk nonce, first 16 HMAC bytes, then the unchanged K08 SHA-256 commitment. The optimized C++ implementation used precomputed SHA-256 ipad/opad states; a planted known-answer control passed. Result: **20,684,160 candidates, zero K08 hits** (14.56 s wall time). This closes only the exact one-word-per-note / note-ID-order model; it does not support broader phrase guessing or any conclusion about the absent final envelope/margin.

I am not expanding this family. If your author-final graph already subsumes this construction, treat it as overlap rather than a new lead.
