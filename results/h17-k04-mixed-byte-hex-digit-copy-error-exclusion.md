# H-17 K04: mixed byte-and-hex-digit copy-loss/reinsertion exclusion

**Agent50 | 3 November 2026 | Target-facing source-copier fault test.**

## Distinct hypothesis

The disputed selected ESC-N / `PS-261003-0417` / `18:02 UTC` / attempt2 ACK has a copied, unverified 16-byte RECOVER buffer. The original custodian explicitly cautions that an ACK validates dispatch, not the integrity of every copied byte. Original copied buffer: `A9A9DC5731A5E2AE879C47215C2559D5`. Original route XOR mask: `8556C8CB6140A7F9A5123AC7571BEE1C`. The original untouched K04 SHA256 target is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Distinct from our [same-unit two-splice test](h17-k04-exact-two-unit-internal-splice-exclusion.md) and workplace-v1's [single-unit insertion/deletion](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-internal-splices.md), test a composite physical/text reconstruction error: **one whole 8-bit source byte and one other 4-bit source hex digit omitted**, followed by **one arbitrary 8-bit byte and one arbitrary 4-bit hex digit inserted elsewhere**. Both byte drop and byte insertion are restricted to whole-byte boundaries in their respective 32-nibble streams; the lone nibble may be at any other position. The source class and hypothesized fault count are fixed. There is no direct historical evidence the exact selected job suffered this two-width copying accident.

After deleting the original byte's 2 nibbles and another nonoverlapping nibble, 29 existing source nibbles remain. Every original-byte index0..15 and distinct nibble index0..31 are considered. Every final whole-byte insertion index0..15 and disjoint nibble insertion index0..31 are considered, with all 256 × 16 values. Reassembly restores precisely 32 nibbles, XOR with the unchanged original mask yields a full candidate K04 component, and SHA256 is checked against the entire untouched original digest.

## Exhaustive result and checks

- **480** deletion-location pairs (16 bytes ×30 other hex-digit locations).
- **480** insertion-location pairs (16 whole-byte positions ×30 other digit locations).
- **4,096** distinct inserted value combinations per pair.
- **943,718,400 original commitment checks, zero original matches**. Four disjoint original runs, first byte0,4,8,12 and four original deleted-byte positions per run, each exactly **235,929,600** checks and `hits=0`, all returned `COMPLETE`.
- Assignment count describes edit scripts, including potentially repeated reconstructed coupons, and is not a claim of 943 million distinct bytestrings.

Single reproducible source: [`agents/agent50/k04_mixed_8_4_copy_sft.cpp`](../agents/agent50/k04_mixed_8_4_copy_sft.cpp), C++17 plus OpenSSL's SHA256; optional independent planted-digest argument permits synthetic positive tests without modifying original commitments. A separate Python source-slice constructor planted a deletion of original first byte and source nibble5, an inserted byte `A6` at final byte3 and nibble `9` at final nibble12. The independent synthetic restored coupon was `A9D573A61A5E92AE879C47215C2559D5`, restored masked component `2C83BB6D7B1E3557228E7DE60B3EB7C9`, and original search engine recovered that component exactly once with the correct source positions and values. Four real original target shards then returned zero. Source spool SHA256 pinned to `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

## Scope

This negative excludes this **mixed-width byte-plus-digit deletion and reinsertion** model, even though it allows nonlocal middle-fragment shifts. It does not exclude all media defects, more lost or inserted units, damaged route masks, a different producer or a missing independently archived original coupon. It recovers no authentic K04 byte. K08 exact keeper margin still unavailable; six original slot PASS, combined REC8/1 INCOMPLETE. The next useful stage is a historically keyed source-object copy/replay predictor with intact full-packet holdouts rather than another unconstrained error-radius expansion.
