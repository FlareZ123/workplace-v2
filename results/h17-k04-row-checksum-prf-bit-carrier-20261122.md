# K04: one checksum or keyed-PRF bit per ordinary print job

**Agent 3 | 22 November 2026 | Conditional complete-value negative.** Original six accepted components remain PASS; K04/K08 remain MISSING and REC8/1 combined is INCOMPLETE.

## Distinct physical-emission hypothesis

The 128 original ordinary printer ACK1 jobs PS-261003-0300 through 0427 supply exactly 128 complete 16-byte packets. A possible 128-bit issuer would convert each routine packet into **one fixed checksum-output bit**, packing 128 chronological bits into the selected RECOVER coupon. Unlike the previous raw-packet bitplane, separable parity, and dense-key matrix studies, this is a nonlinear per-packet compression through conventional checksums, cryptographic digests, or keyed HMAC. There is **no original documentation** asserting this issuer. The selected copied ACK2 bytes do not enter candidate synthesis.

Original source SHA256: printer `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, route `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`, acceptance `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

## Exact complete-value test

Four fixed serializers of each original packet: native, reverse all bytes, reverse bytes inside each 32-bit word, and reverse 32-bit word order. For each serializer, apply eight checksum/digest functions (CRC32, Adler32, CRC16-CCITT with initial FFFF, MD5, SHA1, SHA256, BLAKE2s, BLAKE2b). Select one fixed bit position per job and pack the 128 row bits using both chronological directions and both byte bit-orderings. Independently, use HMAC-SHA256/512 on each serialized packet under **eight original 16-byte keys**: six SHA256-accepted slot values, original K04 XOR mask and K08 nonce. Complete 16-byte outputs are XORed against the exact route mask; the **full original K04 SHA256 commitment** `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0` is checked.

| Candidate family | Complete source-selected assignments | Historical commitment matches |
|---|---:|---:|
| Per-row checksum/digest bit | 22,272 | **0** |
| Per-row source-keyed HMAC bit | 98,304 | **0** |
| Combined | **120,576** (120,337 distinct 16-byte values) | **0** |

A planted full source-selected CRC32-bitstream coupon is independently SHA256-checked and recovered exactly once. The source extraction asserts 133 rows, 128 contiguous routine job identifiers, unique selected job identity and six original accepted slot hashes. The source-pinned read-only [Python SFT](../agents/agent3/k04_row_checksum_prf_sft.py) runs with standard library against `resources/` or the original ZIP. The original 46-file ZIP extraction was tested locally; the committed implementation is source-equivalent.

## Consequence

No accepted K04 component is produced by this explicit source-keyed per-row checksum/PRF **one-bit** carrier family. It does not constrain arbitrary per-row proprietary encodings, lost native printer payload, selected-stage producer, or any actual coupon bit. This is a small bounded experiment, **not** an authenticated historic emitter or invitation to search free 128-bit row-selector masks. Prefer new physical-coupon witness, independently predictive printer producer or source-backed complete K08 phrase rule. Original evidence, candidate file, verifier and acceptance were not altered.
