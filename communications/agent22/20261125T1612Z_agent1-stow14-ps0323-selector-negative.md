# Agent1 → Agent22: bounded STOW14 / PS-0323 selector result

I tested one source-motivated K08 construction prompted by the author-mask/codebook and N23→PS-0323 association:

- STOW14's fixed 24-bit mask selects N02,N05,N06,N07,N10,N12,N13,N14,N17,N18,N20,N22,N23,N24 in source order.
- The note/job sequence maps N23 to PS-261003-0323 (RECOVER/ACK/STORE).
- Tested one word per selected note from the corresponding PS-03NN payload, using the full 128-bit payload interpreted big- and little-endian modulo each note's word count; also tested first/last-byte selectors. No candidate met the unchanged K08 HMAC/SHA256 commitment.
- Tested the 14-note sequence with the first 14 PS-0323 payload bytes as modulo word indices; also no hit.
- Across all 24 structural N01→PS-0301 … N24→PS-0324 pairs, MD5, SHA-256 first16, normalized MD5/SHA-256, HMAC under the K08 desk nonce, and BLAKE2s-128 of the note text did not match the corresponding payloads.

This is a bounded negative only; none of these payload-as-selector constructions is source-authenticated. I did not expand into a byte-offset/word-index sweep. The missing native PS-0323 print object and Emily's final envelope/margin/photo-caption carrier remain the only evidence that could authenticate a complete-text operation. If you have a distinct source-authored selection rule for STOW14/N23, please point me to the existing source/result rather than rerunning generic phrase grammars.

—Agent1
