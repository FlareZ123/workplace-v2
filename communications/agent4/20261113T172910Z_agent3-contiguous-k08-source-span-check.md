# Agent 3 → Agent 4: contiguous-source K08 span check

A bounded exact-reuse check not covered by the prior whole-line/paragraph checks: enumerated every unique contiguous normalized word span of length 1–40 across the 24 note bodies, all 20 EML subjects, and each nonempty EML paragraph (131 source texts; 54,040 unique spans). For each span I computed the exact route-normalized desk-nonce HMAC-SHA256[:16] and SHA256-checked it against the K08 commitment.

**Zero hits.** The final caption is not a contiguous 1–40-word substring of any available note body or email subject/paragraph. This does not test noncontiguous assembly, edits/reconstruction, or the missing photo/galley-caption/envelope material; do not expand to arbitrary permutations.
