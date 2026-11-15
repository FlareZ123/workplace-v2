# K04: complete 32-bit common-word XOR corruption search, original source

**Agent14 | 15 November 2026 | 4,294,967,296 full SHA256 checks, zero original K04 matches, one planted positive.** K04/K08 remain missing, six other components individually accepted, combined REC8/1 incomplete.

## Distinct complete-object mechanism

The retained selected PS-261003-0417 RECOVER ACK attempt2 is `A9A9DC5731A5E2AE879C47215C2559D5` (18:02Z), but MAIL16 and the custodian note do not certify the physical coupon bytes. An error affecting a **repeated four-byte copy-stage mask across all four 32-bit lanes** would alter more than the four arbitrary byte positions excluded by the earlier 1,820-support exhaustive research. Freeze the independently recoverable 32-bit common-error hypothesis before querying the commitment: for every unsigned x in the complete interval [0, 2^32), construct `P[x][i] = ACK2[i] XOR BE32(x)[i mod 4]`, then derive the proposed component `C[x] = P[x] XOR 8556C8CB6140A7F9A5123AC7571BEE1C`. Check the unchanged **full** K04 SHA256 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

This is a conditional fault model. **No historical printer source attests a repeated-word XOR mask**, and no inference that this was the real fault follows from its test. The candidate domain is nevertheless exact, complete, and distinct from all at-most-four-byte repairs. Reversing the four-byte word's endianness or shifting its repeated pattern by any fixed byte phase merely reindexes the same full 2^32 domain, so those variants are exhausted by this one run.

## Original execution and controls

- Local source: unchanged `evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The program also verifies the exact selected ACK line, original route mask and original K04 acceptance digest. Neither archive nor canonical candidate is modified.
- Optimized single SHA256 padded 16-byte block, 1,024 independent comparisons of complete OpenSSL SHA256 against its one-block compression implementation, **all pass**.
- Exhaustive domain partition: 256 disjoint high-byte shards, each 16,777,216 32-bit word values, no omission or duplicate; 256/256 logged complete with zero original hits.
- One full planted synthetic digest from genuine mask `0xC1A071F3`; recovered **exactly once** in high-byte shard **193**. Original commitment remained unchanged.
- Final original output: `FINAL checked=4294967296 original_hits=0 synthetic_hits=1 seconds=58.523`; five local worker threads. Reconciled entire 256-shard log, exact set {0..255}, and all original/plant counts. Local log SHA256 `fa4c10368dbd21faa647960b85c65f80cd111b15cee72c7de9890a9a9dcd600a`.
- [C++17/OpenSSL/OpenMP source-pinned SFT](../agents/agent14/h17_k04_periodic_word_xor_sft.cpp). Run with original resource root and numeric 256 for full domain, using a compiler with OpenMP and libcrypto.

## Consequence

**No original K04 component is reachable by a uniform repeated 32-bit XOR copy-stage error from the disputed selected ACK2 source.** This closes exactly that full model; arbitrary masks, variable masks, actual physical coupon data, a different printer emitter, or unrecorded source fields remain outside it. It establishes no authentic physical coupon bit. K08's literal author-final phrase remains unknown, and the combined key cannot be verified.
