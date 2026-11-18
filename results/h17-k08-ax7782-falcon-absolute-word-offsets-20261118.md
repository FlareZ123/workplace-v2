# K08: AX-7782 checkpoints as Falcon absolute word offsets

**Agent 20 | 18 November 2026 | Closed negative for the four frozen interpretations.**  
The original K08 commitment, routing, acceptance file, verifier and canonical candidate were not changed.

## Question

Agent 9 proposed a finite cross-record hypothesis: the eight AX-7782 attempt-2 chunk checkpoints, in `seq=0..7` order, may be eight absolute word offsets into the pinned 1889 *Falcon on the Baltic* normalized text. This is explicitly conjectural; the transfer audit defines the values as per-chunk checkpoints, not word offsets, and does not establish an AX-7782 → book → Emily-caption source relationship.

## Source pins and controls

- The exact eight checkpoints were independently read from `resources/evidence/transfers/transfer-audit.jsonl`, filtering `transfer=AX-7782, kind=CHUNK, attempt=2` and sorting by `seq`:
  `8947 CEDC B9CC 73BA B7E8 7BE6 3302 C5C9`.
- Joined checkpoint bytes: `8947CEDCB9CC73BAB7E87BE63302C5C9`.
- The pinned normalized book is `work/h17_falcon_1889_normalized_words.txt`, 81,392 words. Its word-stream SHA-256 excluding the trailing newline is `36997e8cf827a0c0ddade6104b8d63c5e462e69749653ce009e5e50ce4fcce66`; committed Git blob `782d4687c98cdc0012e56447fcc4dfa77728603c`.
- The K08 nonce is `5F933DA6A1BD03C32DA5CBC25344F497` and the unchanged target is `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.
- The source normalization is lowercase, replace non-ASCII-letter/digit/whitespace characters with spaces, collapse whitespace and trim.
- Positive known-answer control: N02 normalizes to `a good watch leaves the room ready for the next pair of hands` and reproduces HMAC16 `BF889359B0303F2B2B2FD96AE841210B`.

## Complete candidate check

The eight raw bytes were interpreted as unsigned 16-bit words in both byte orders, with both zero-based and one-based indexing. Each resulting eight-word phrase was normalized, HMAC-SHA256 keyed by the original nonce was truncated to 16 bytes, and the resulting component was SHA-256 checked against the original K08 commitment.

| Interpretation | Eight normalized words | HMAC16 | SHA-256 commitment check |
|---|---|---|---|
| Big-endian, zero-based | `manner so hot were there navigated locks that` | `EA8D8A7DFD816D854CD011B7FFCA22E4` | `2e3d5a35dc3e485bd32d5b6600798975d3441a5d247beab8a83b76ffc624cbf6` |
| Big-endian, one-based | `original babel then animals life had tarred me` | `AFC84D55F0499B66B2CAD55FFB1F9140` | `8d446c9eed9effe7312b67052374843a528f3f32366e501982edd2095daf1fe2` |
| Little-endian, zero-based | `my the the the germany how danish peter` | `5D4D76ED73464B56052BEC8F61F65371` | `0d275379c83c0916520fbc90eb9978b213f717e4664b8be69a965c52b7848e09` |
| Little-endian, one-based | `that shore so in like perceived shallowest two` | `FDCC7401E9F8A3C8E4ED654F2357C168` | `1442a4ba1a092eb1df1d4ed0c131d79153188b93b58a3d80ad607a9795073791` |

**Result: 0/4 original K08 commitment matches.** The four candidate phrases are complete, in-range and reproducible; none yields the accepted 16-byte component.

## Boundary

This closes only the frozen AX-7782-checkpoint → eight unsigned u16 absolute Falcon word offsets → K08 construction. It does not establish the Falcon as the physical map-back book, prove the checkpoints were intended as word positions, rule out page/word or other source-indexed selectors, or recover Emily's final wording. Do not widen this into arbitrary byte permutations, offset arithmetic or another book search without an independently authenticated source rule.
