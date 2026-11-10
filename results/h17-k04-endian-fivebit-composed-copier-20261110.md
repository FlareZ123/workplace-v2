# K04: four physical-copy byte orientations composed with up to five bit faults

**Agent 49, 10 November 2026. Original complete-coupon target test: 1,102,336,132 candidate assignments, zero accepted.** The original REC8/1 remains six slots PASS; K04/K08 MISSING; combined INCOMPLETE.

## New target-reaching model and source limits

The 18:02 UTC selected north route `PS-261003-0417`, `RECOVER` attempt-2 `ACK` copied buffer is `A9A9DC5731A5E2AE879C47215C2559D5`. MAIL-16 warns that its recovered payload has no independent physical-media checksum. N22 calls the office label printer fax-like, and the fleet-register notes paper-feed repairs. These are contextual reasons to test byte-order recapture and sparse bit corruption **together**. They do not show that either occurred historically.

Prior original tests handled endian/byte-grid rearrangement alone, or sparse bit faults in the original copied byte order. This source-defined composition treats the **transformed physical payload as the corrupted stage**, then allows up to five arbitrary bit corrections anywhere in its 128-bit value, applies the unchanged original ESC-N 16-byte route XOR mask, and checks the *entire* official K04 SHA256 digest. The selected buffer is not treated as independently authenticated physical data.

The four frozen byte mappings, applied to the 16 original bytes before the sparse bit errors, are:

1. Reverse bytes inside every 32-bit native word (per-dword endian).
2. Reverse the order of the four 32-bit words (preserve bytes inside them).
3. Reverse all sixteen bytes (combined endian and word-order reversal).
4. Transpose the 4×4 byte grid, representing a row/column raster readout.

Each mapping covers all bit-fault sets of cardinality 0 through 5, with no position restriction. The search does not refit the original mask, modify the source record, or use the target commitment to choose transformations. The original copied order is intentionally excluded because its larger Hamming shells were previously tested.

## Executed original and planted controls

Original spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Original mask: `8556C8CB6140A7F9A5123AC7571BEE1C`. Original K04 target SHA256: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. The executable asserts exact original source hash and unique selected ACK2 source line.

For each of the four mappings, the exact exhaustive Hamming shells have sizes: weight0 **1**, weight1 **128**, weight2 **8,128**, weight3 **341,376**, weight4 **10,668,000**, weight5 **264,566,400**. Thus there are **275,584,033 complete SHA256 checks per mapping** and **1,102,336,132 original complete-coupon assignments** in total. There are zero K04 target matches at every weight in all four mappings. Counts are assignments rather than globally distinct values across mappings.

The initial original run, which had the identical generator and target path, completed all four models and produced the final line:

```text
FINAL original complete coupon commitments=1102336132 original_hits=0
```

The updated permanent source also executes a **full three-bit shell (341,376 candidates)** for each of four independent planted complete source coupons, requiring exactly one full-hash synthetic match per mapping. All four positive controls and their wrong-coupon negative checks passed. The enhanced source was independently compiled and the synthetic shell mode executed. Original run log SHA256: `b25c679b05c171cba2abb40bace19755f58418d3332c1599c607ec4d6f78060f`. Enhanced original source SHA256: `c38242b8b763578c3bc1e908b412526d9c445fe295943cd62ebd30c21abb4d14`.

**Permanent reproducer:** [portable C++17/OpenSSL original-source SFT](../agents/agent49/k04_transport_bitfault_sft.cpp). From the root of a repository checkout, compile with any C++17 compiler and OpenSSL's libcrypto and run with no argument; the original spool path is `resources/evidence/print/spool-reconstruction.log`. Optional first argument supplies another path for equivalent original ZIP extraction. The optional second argument `--self-test` runs only the planted exhaustive three-bit checks.

## Interpretation and decision

This closes exactly four composed orientation-plus-at-most-five-bit-fault hypotheses on the *selected copied K04 payload*, for the original payload-before-XOR reduction stage. It does not cover other byte/grid permutations, nontrivial nonlinear recoding, a different archival source, longer corruption, a changed route mask, or an independently generated authentic physical coupon.

The 1.1-billion negative is a bounded target-facing calculation, not an original selected-medium witness. **Do not extend the speculative Hamming radius automatically.** A stronger next route needs an original selected physical coupon source, a producer with whole-object original controls, or different source-indexed missing native data. K08 author-final phrase remains a separate unresolved exact-language component. All originals, route, verifier and canonical submission remain unchanged.
