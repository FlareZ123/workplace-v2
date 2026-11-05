# H-17 printer bit-plane carrier search: complete K04 and K08 candidates

**Agent 30 | 5 November 2026 | original commitments unchanged | neither missing slot recovered.**

## Distinct alternate source mechanism

The recovered printer export contains 128 regular five-minute rows, plus five irregular later rows; each original PAYLOAD is exactly 16 bytes. A conceivable bitmap/serial transport is a single bit plane of each payload byte, rather than a normal 16-byte opaque field. This representation differs from raw-byte/hex scanning, per-byte XOR and codepage decoding, periodic-key text decryption, ordinary printer LABEL/HMAC alignment, and byte-mosaic copy repairs.

The test asks two separate complete-candidate questions:

1. Could a retained independently copied printer bit-plane stream contain the original physical 16-byte ESC-N coupon as a contiguous 128-bit packed window? Each decoded 16-byte window is XORed with the original route mask and hashed against the full unchanged K04 commitment.
2. Could the bit-plane stream contain verbatim terminal-caption plaintext, encoded as seven- or eight-bit ASCII in an otherwise opaque printer packet stream? Every sufficiently long printable run is normalized under the original route rule; all qualifying contiguous 2..24-word subphrases are reduced with the original desk-nonce HMAC16 and full unchanged K08 commitment.

The original sources do not assert that the printer encoded the keeper caption this way, or that any separate printer payload reproduced the physical selected coupon. This is an alternate representation hypothesis tested directly rather than asserted historically.

## Fixed original inputs and covered views

- Printer original resources/evidence/print/spool-reconstruction.log SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.
- Crew-note original SHA256 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb.
- Event-selected copied packet uniquely identifies 2026-10-03T18:02:00Z / PS-261003-0417 / attempt 2 / ACK / RECOVER, payload A9A9DC5731A5E2AE879C47215C2559D5. It is withheld from all carrier groups rather than treated as an authenticated physical original.
- Six source packet groups: all remaining packets, LABEL, STORES, remaining RECOVER, pre-18:00 packets, and the two same-job REQUESTED attempts; cardinalities **132, 52, 41, 39, 128, 2**.
- For every group: chronological/reverse row order, forward/reverse byte columns, row-major/column-major transposition, all eight bit positions, original/complement bits, 7/8 bit character widths, original/reversed bit order within character, and each legal alignment phase. Exactly **23,040 full derived byte streams**.

The K08 textual candidate rule requires a decoded ASCII-allowed run of 14+ bytes and at least two normalized words of length at least three. This intentionally excludes one-word fragments and non-ASCII, encrypted or otherwise compressed captions. K04 windows have no plaintext requirement.

## Executed result and positive controls

| Exhaustive finite test | Original complete candidates checked | Commitment matches |
| --- | ---: | ---: |
| K04 all distinct 16-byte packed source windows XOR original mask | **2,333,824** | **0** |
| K08 distinct normalized printable source spans under actual HMAC16 reduction | **74** | **0** |

The complete original-source test ran locally with the unchanged archive. In the initial pilot, no printable extracted source runs of 24 or more contiguous ASCII characters contained a space. In the final narrower candidate generator, all 74 qualifying source-derived phrases failed the unchanged K08 full SHA commitment. No bit of the genuine selected K04 coupon or verbatim final K08 caption word is authenticated.

Positive controls: the exact original Emily N02 draft gives known HMAC16 BF889359B0303F2B2B2FD96AE841210B; an independently planted full N17 standby inscription hidden in bit 0 of synthetic 16-byte packet rows is read back as the complete old caption, and the synthetic full K08 component commitment passes; an independent planted full 16-byte synthetic coupon similarly survives bit-plane encoding and the complete masked K04 commitment check. These are algorithm controls, not historical finds.

The tested, source-pinned, standard-library single-file [reproducer](../agents/agent30/k04_k08_spool_bitplane_small_sft.py) was pushed as Git blob SHA f92dee29d6b5191f6cb6202e8e5b64ae5cb9fb2c, byte-identical to the executed local SFT. It asserts both original source hashes, selected event, group sizes, 23,040 views, all candidate cardinalities and zero matches.

## Boundaries and recovery implications

This rules out only the specified single-bit-plane 7/8-bit sequential transport and selected-intact-packet alternative-coupon carrier family. It does not rule out interleaved multiple bit planes, nontrivial printer codecs, an external physical original, author-edited wording absent from this export, or the conditional MT stage model already identified elsewhere. The absence of a detected literal is consistent with the documented source provenance gap; it does not establish that recovery is impossible.

The official six K01/K02/K03/K05/K06/K07 components still PASS; K04 and K08 remain missing and combined REC8/1 remains INCOMPLETE.

**Next useful direction:** exploit a causal relation that predicts a complete independent selected-stage object or final authored phrase. Retire additional arbitrary bit-plane variants unless a record indicates the printer encoding.
