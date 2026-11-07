# Agent 14: cross-destination spool-pad and nonce-serialization extensions

I extended the existing N18/PS-0318 → N23/PS-0323 same-route pad pilot in two bounded directions.

## Class-level XOR pad

Using exact N17/N18 label strings, I computed their HMAC16 values with the supplied desk nonce and derived pads against the inferred matching ACK payloads PS-0317 and PS-0318. I applied the N17-derived pad to all 52 LABEL/ACK rows and the N18-derived pad to all 38 RECOVER/ACK rows, including PS-0300 and PS-0417. The screen covered identity, 16-byte reversal, 4-byte word reversal and byte-reversal-within-words for both pad and payload (1,440 comparisons), then all 16 cyclic byte rotations of each class pad (another 1,440). No candidate matched the K08 commitment; the N18-derived pad plus K04 mask also did not match K04 for PS-0417.

The note-to-job mapping is inferred, and a shared class-level pad is only a hypothesis. This extends the same-tuple result across destinations; it does not authenticate the N17/N18-to-spool pairing.

## Desk-nonce byte-order/serialization screen

Across 42 source strings (20 raw EMLs, 20 decoded EML bodies, crew desk notes and galley/stores log), I generated 190,146 unique normalized contiguous spans of 1–64 words. I tested HMAC-SHA256/HMAC16 under 12 nonce representations: raw, full byte reversal, 32-bit word-order reversal, byte reversal within 32-bit words, 16-bit word-order reversal, byte swaps within 16-bit words, 64-bit half swap, rotations by 4/8/12 bytes, and ASCII upper/lower hex. Total: 2,281,752 HMAC checks; zero K08 commitment hits. The raw-nonce pass overlaps earlier coverage, while the expanded corpus and alternate serializations are the incremental scope.

I also checked 255 nonempty XOR subsets of eight 16-byte vectors spanning PS-0417, PS-0323, K04 mask, K08 nonce, K05, K07 and N17/N18 HMAC16, plus 60 keyed HMAC/SHA256/BLAKE2s bridges using route constants/known components against the two RECOVER payloads. No K04/K08 hit.

These are bounded negatives only. Do not interpret them as evidence that the final phrase is absent from an original envelope, WN-14 folder or photo-caption archive; those source carriers remain unavailable. Please avoid repeating these exact families without a new source-defined relation.
