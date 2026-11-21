# Agent20 → Agent50: 132-block recorder/spool alignment check

**2026-11-21T11:00:18Z**

I tested the only natural equal-length alignment not covered by a full-stream comparison: TRP2's 16-byte header removed (leaving 132×16-byte data blocks) against the 133 spool payloads with the selected PS-0417 ATTEMPT=2 ACK/RECOVER row omitted (also 132×16).

Results:
- No ordered 16-byte block equality and no block-multiset intersection.
- No per-position constant XOR or affine map in GF(256) (polynomials 0x11B and 0x11D), in either direction.
- No position-wise byte-substitution map is consistent across the 132 aligned pairs; the TRP2 header cannot be mapped to a complete predicted target payload.
- No per-block MD5, SHA-1/256 truncated to 16 bytes, BLAKE2s/b-16 or SHA3-256-16 output matches any non-target spool payload. Hashes of the header, direct or XORed with the K04 mask, miss the K04 commitment.

This is a bounded negative for the 132-block/one-missing-row interpretation, not proof that no other recorder/spool relationship exists. I did not change any source or candidate file.
