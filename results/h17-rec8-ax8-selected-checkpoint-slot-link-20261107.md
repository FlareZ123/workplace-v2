# H-17 REC8/1: selected AX-7782 eight-chunk to eight-slot carrier gate

**Agent 10 | 7 November 2026 | Original-source negative, no recovered K04 or K08 component.**

## Attack question

The independently selected, committed `AX-7782` transfer has **eight numbered chunks**. The recovery envelope has **eight numbered components**. This count and common incident object suggest a concrete alternative to attempting lost physical-text reconstruction: suppose each two-byte chunk checkpoint recorded or deterministically generated its slot's sixteen-byte component, or retained a short CRC16 of that component. If an authentic rule predicted independently recovered components K01, K05 and K06, it could be frozen and applied to missing slots K04 and K08.

This is a **new conditional cross-archive join**, not a statement that chunk sequence numbers mean component numbers. The preserved transfer note describes opaque checkpoints for whole 1 MiB chunks and does not identify them as REC8 slot fingerprints. The three original direct-byte components are chosen as intact controls because K02, K03 and K07 have separate hash reductions.

## Frozen source and source-only controls

Original `evidence/transfers/transfer-audit.jsonl` SHA-256: `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`. Select the sole genuine non-dry-run AX-7782 COMMIT and the highest-attempt CHUNK for each seq 0..7. All selected attempts are 2; their sixteen unmodified checkpoint bytes concatenate to `8947CEDCB9CC73BAB7E87BE63302C5C9`. The unrelated selected ESC-N copied ACK is never read, and neither missing original commitment is consulted during construction.

The three complete, independently established source outputs are K01 `049AAB2E1CDE7A82CD7C60234303C91A`, K05 `FF8B78200A56E8586DCDA00EF01E4572`, and K06 `5DBF40EE52FAAED9A536D3326CF0D95A`. The original `acceptance.json` SHA-256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f` is asserted.

The **complete generator** tests twelve explicit two-byte-to-sixteen-byte functions: octuple raw repetition; MD5; first/last SHA-256 half; first SHA-512 half; BLAKE2s-128; HMAC-SHA256 first-half keyed by original K08 desk nonce or original K04 route mask; and first SHA256 or nonce-HMAC half over `slot-label || checkpoint` or `checkpoint || slot-label`. Every function is tried across eight sequence cyclic offsets, normal/reversed seq direction and both byte orientations: **12 x 8 x 2 x 2 x 3 = 1,152 complete sixteen-byte historical predictions**.

The **fingerprint** test uses seven conventional CRC16 configurations: CCITT initial 0/FFFF, X25, KERMIT, IBM initial 0, MODBUS and DNP, with the same index and byte layouts: **7 x 8 x 2 x 2 x 3 = 672 original sixteen-bit controls**.

## Executed original outcome

| Test | Original source comparisons | Exact matches |
| --- | ---: | ---: |
| Complete sixteen-byte checkpoint expansion | 1,152 | **0** |
| CRC16 of authentic complete K01/K05/K06 byte sources | 672 | **0** |

A separate deliberately planted *whole-object* chain constructed with independently calculated SHA256 values was reconstructed by the same source-side scanner across three slot positions, including a nonzero phase and reversed source bytes. An independent `binascii.crc_hqx`-generated three-slot CRC chain was also recovered. Original transfer hash and selected chain assertions passed, as did standard CRC known-answer vectors.

## Boundary and next move

The eight-chunk/eight-slot coincidence supplies no source-authenticated bridge under these **nineteen** explicit transform families. A stronger reconstruction requires actual chunk-to-component identity evidence, a shared content-derived key, or an independently predicted entire historical slot before applying it to K04/K08. These negatives do not exclude an arbitrary unknown chunk serializer, longer data dependencies or independent physical source.

**Accepted state remains six original PASS values; K04 and K08 are MISSING; combined REC8/1 is INCOMPLETE.** Original archive, verifier, mask, nonce and canonical candidate are unchanged.

Reproducer: `agents/agent10/k07_8chunk_slot_link_sft.py`.