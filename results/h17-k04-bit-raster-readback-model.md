# K04 experimental copier bit-raster readback: 123,028 complete candidates rejected

**Agent 25, 2 Nov 2026. Source-anchored exploratory model, no original K04 recovery.**

## Mechanism

The original 3 October crew note N22 says the label printer sometimes behaved like a fax; original MAIL-16 separately warns that the retained printer buffer has unverified payload integrity. The selected original copied ESC-N / PS-261003-0417 / RECOVER ACK attempt2 at 18:02Z is `A9A9DC5731A5E2AE879C47215C2559D5`. The recorded XOR mask remains `8556C8CB6140A7F9A5123AC7571BEE1C`. These clues **do not** prove a raster-copy error, but motivate testing one complete, finite, physically interpretable family that changes bits throughout all 16 bytes rather than changing a few local bytes.

View the 128 retained payload bits as a rectangular raster of height 1,2,4,8,16,32,64 or128, width 128/height. Read input and output in one of four scan modes (row-major, row-major serpentine, column-major, column-major serpentine), with independently selected within-byte bit order. Permit whole-image reflection on each axis, row/column transpose, and arbitrary cyclic pixel-origin shifts in six nondegenerate rectangular shapes. All map 128 source bits bijectively to 128 candidate bits, preserving only the bitmap's bit multiset. Deduplicate complete reconstructed 16-byte strings, then XOR each one with the **unchanged** original mask and compare the SHA256 digest to the **unchanged** original K04 slot commitment.

## Original result and scope

A first geometry scan generated **230 distinct 16-byte candidates**. Extending with the six raster sizes' cyclic row/column offsets generated **123,028 distinct complete payload candidates**. All 123,028 were tested against the original K04 hash: **0 matches**. An in-memory synthetic planted candidate was recovered exactly once by both the base and extended procedure. Original spool SHA256 is pinned to `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Read-only [single-file test](../agents/agent25/k04_bit_raster_sft.py) reproduces the original data selection, the complete transformations, synthetic control and exact counts. The local equivalent SFT ran successfully; no original source or verifier was edited.

This is a new **bit-level 2D scan-order** fault model. It differs from the previously exhausted bit insert/delete and source-byte/word permutations, and from v2 Agent31's **byte-lane** transpose. The test excludes only these complete bit-permutation geometries applied to the copied ACK with the mask held fixed. No actual physical raster format has been authenticated, and the result supplies no original target bit. It leaves arbitrary copier corruption, alternate producer generation, and other nonpermutation transformations unresolved. K08 exact author-final caption is likewise absent; the original six PASS slots and combined INCOMPLETE accounting remain unchanged.

## Independent original-mask raster stage

A distinct end-to-end copier/transcription hypothesis holds the selected recorded ACK payload fixed and applies exactly the same 128-bit image-raster reserialization to the original 16-byte route **mask** instead. This is outside the earlier source-ACK permutation class and outside Agent30's original-mask **byte-lane** permutation model.

Locally executed source-equivalent test generated **230** base distinct reconstructed masks and **123,204** complete distinct masks after all cyclic scan-origin shifts. For each candidate, the source ACK remains exact and only the mask moves; the original K04 SHA256 commitment was unchanged. **0/123,204 matches**, and an independently planted synthetic mask passed exactly once. The same repository [single-file SFT](../agents/agent25/k04_bit_raster_sft.py) now tests both stages and their separate synthetic controls.

**Combined scope:** 246,232 distinct complete original-commitment candidates across independently transformed PAYLOAD and MASK stages, none accepted. We did not permit applying two unknown bit-rasters simultaneously, choosing arbitrary per-byte faults, or change the official route/acceptance. Neither transformed family is historically proven; both are bounded source-copy fault tests with no verified K04 coupon gain.

## Shared reserialization and image-polarity extension

A third stage treats the full XOR-reduced component as one scanned 128-bit image (equivalently, applies the same bit permutation simultaneously to both PAYLOAD and MASK). This yields **123,072 distinct** transformed components. It, too, produces **zero original K04 hash matches**; a planted transformed component is correctly recovered once. A separate binary image-polarity inversion was tested across each of the **three** stages, each with zero original hash matches.

Total independently evaluated stage-and-polarity assignments: **738,608** (payload 123,028×2, mask 123,204×2, combined 123,072×2). Some complete values can coincide across stages, so this total counts assignments and should not be described as 738,608 globally unique values. These source-defined low-description-length bit-raster hypotheses are exhausted at their explicitly tested geometry. Other copier faults and the independently printed original remain unknown.
