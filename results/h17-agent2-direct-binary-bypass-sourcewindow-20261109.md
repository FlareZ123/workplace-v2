# H-17: direct K04/K08 binary-component reconstruction from original source substrings and parity shares

**Agent 2 | 9 November 2026 | Original commitments unchanged | Both missing slots still unresolved.**

This is an exploratory alternative to guessing the missing Emily caption or trusting the selected 18:02 copier buffer. In both tests, every construction yields an **entire 16-byte component** and is checked against the original complete SHA256 commitment; no partial digest matches are treated as recoveries. Both tests exclude the selected `PS-261003-0417` attempt2 ACK copied buffer from inputs.

## Model A: small cryptographic digest of a retained source substring

A real printer might emit an opaque 16-byte ticket as the MD5 digest or a selected 16-byte SHA256 half of an existing source record. Equally, the K08 component might have been copied from a source-derived digest rather than derived from the missing personal text. **The archive does not identify either of these mechanisms.** This test checks complete candidates directly.

- Inspect the **40 original plaintext evidence files**, excluding the encrypted BX25-08 PDF and binary recorder (handled separately below). Explicitly remove only the unauthenticated selected 18:02 spool line; retain other unselected original spool buffers.
- Enumerate every contiguous original byte substring of lengths 1..256 inclusive: **25,504,512** source windows, partitioned into eight disjoint file-index shards.
- For each window, emit **MD5(bytes)**, **SHA256(bytes) first16** and **SHA256(bytes) last16**, totaling **76,513,536** complete 16-byte values.
- Check both candidate routes: K04 = emitted bytes XOR original mask `8556C8CB6140A7F9A5123AC7571BEE1C`; K08 = emitted bytes directly. Compare complete `SHA256(K04)` and `SHA256(K08)` to the two unchanged original 256-bit commitments.

**Original outcome: zero full K04 or K08 hits across 153,027,072 complete acceptance comparisons.** All eight file shards reported zero with no gaps in the sorted file-index intervals `[0,4), [4,15), [15,29), [29,31), [31,32), [32,39), [39,40), [40,42)`. These intervals correspond to 42 regular evidence files including two explicitly excluded binary/encrypted formats. A planted substring MD5 payload passed both full-component reduction controls.

Portable read-only C++17/OpenSSL [SFT](../agents/agent2/h17_sourcewide_digest_windows_sft.cpp) reconstructs the exact scan from the unchanged `resources/evidence` tree. The original execution used the unmodified extracted user-supplied ZIP, and the actual eight-shard output counts were reconciled. The single-run C++ reproducer uses a corrected nontrivial full-component positive control and the same full enumeration.

## Model B: three- and four-way XOR from surviving complete source fields

Construct **476 distinct 16-byte carriers** from original source hexadecimal fields; 132 unaffected printer packets; 84 CRC-valid trip-recorder rows and selected natural 16-byte record views; contiguous recorder quartets; transfer checkpoint octets; telemetry 16-bit word octets; six accepted components; HMAC16 of four exactly quoted surviving authored drafts/labels; and route fields. Original printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` and original crew notes SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb` were asserted.

- Check **all C(476,3) = 17,861,900** 3-carrier XORs, each as a raw K08 component and, after XOR with the original route mask, as a complete K04 component.
- Check **C(160,4) = 26,294,360** 4-carrier XORs from the first 160 preserved carriers in source order, under both original complete commitments. This is explicitly a bounded four-way family, not every possible 4-subset of 476.
- Results: **zero** real K04 hits and **zero** real K08 hits in either family. An independently defined planted 3-share witness `(7,39,121)` and 4-share witness `(1,39,67,127)` each produced exactly one complete synthetic positive in both original reduction paths.

The carried local SFT source for this model is recorded in [Agent 2 memory](../agents/agent2/memory.md). Prior Agent47 binary K08 two-carrier tests were a different smaller arity. Neither the preserved source nor the published commissioning route attests a three- or four-share encoding.

## What this establishes

All candidate families above are exhausted for the precise source set and serialization, and **none recovers either missing value**. Their combined original-target comparisons exceed 241 million, but count is no substitute for historical source coupling. The observed no-hit outcomes reject these exact mechanisms only. Neither experiment yields a physical K04 coupon bit, an exact final K08 caption word, or a validated seventh component. The original six slots remain PASS, K04 and K08 MISSING and combined REC8/1 INCOMPLETE.

A productive successor needs an independently discriminating relation between retained records and the selected printer medium or the exact author-final caption, rather than enlarging these unsupported byte constructions.
