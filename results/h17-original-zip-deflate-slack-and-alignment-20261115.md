# H-17 original ZIP DEFLATE slack and alignment carrier test (15 November 2026)

**Agent 43 | Source-pinned original ZIP, 46 compressed file members | K04/K08 original hits: zero.** This tests an alternative complete 128-bit carrier within the source *container* without assuming that the printer buffer or Emily's final prose survived in the extracted member bodies. It is a speculative archive-steganography hypothesis; no original record says the packager encoded recovery components in DEFLATE.

## Source and distinct candidate construction

Exact supplied \`h17-archive-dump.zip\`, 50,526 bytes, SHA-256 \`e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7\`. The original file bodies, routing, commitments, verifier, and canonical submission were untouched.

1. Locate the raw DEFLATE stream in each ZIP local file member using its central-directory compressed length and local header filename/extra lengths. Read all 46 deflated members in original archive order; directory entries are stored, not deflated.
2. Determine trailing unused high bits by flipping successive high bits in the stream's final byte and requiring independently decompressed output to remain byte-for-byte identical to the verified ZIP member. A separate explicit RFC1951 bit-reader prototype independently agreed on every end-of-stream boundary and every uncompressed output size. There are **170 slack padding bits across 46 streams; all 170 are zero**. No nonzero original payload is present in this particular unused-bit channel.
3. A separate, more compact carrier is the 3-bit encoding of each member's trailing-unused-bit count. Forty-six counts form **138 bits**, enough to hold a 128-bit opaque value under a chosen alignment. Freeze the plausible simple layouts before checking the target: normal/reverse member order, high-to-low/low-to-high individual 3-bit digits, every contiguous 128-bit offset 0..10, forward/reversed 16-byte order, direct or XOR the original K04 mask. This is **2×2×11×2×2 = 176 complete 16-byte candidate assignments**.
4. Hash each assignment with SHA-256 and compare separately with the **unchanged original** K04 and K08 full slot commitments: **352 target comparisons, zero matches**. A separately constructed 128-bit synthetic length-channel message is recovered by the identical candidate constructor, providing a planted positive control.

The exact 46 three-bit values (in source order) are:

\`\`\`
6 1 4 2 5 4 7 0 6 4 3 3 7 5 2 3 1 4 5 6 7 1 1
1 5 0 7 6 3 0 4 6 3 2 5 1 7 3 3 4 4 3 3 6 7 0
\`\`\`

## Reproduction and boundary

[Standalone Python standard-library SFT](../agents/agent43/h17_zip_deflate_channel_sft.py). Pass the unchanged original 50,526-byte ZIP path as the sole argument. It asserts the original whole-archive SHA, exact member count and 170 slack bits, decompression agreement, all-zero original unused padding, exact 176 layouts, zero authentic full-slot hits, and the planted 128-bit length-channel control. A synthetic high-bit perturbation additionally confirms those bits really are ignored by the DEFLATE decoder.

This **closes only two precisely defined optional ZIP-carrier encodings**. The distribution of unused-bit *lengths* is a property of the source-compression bitstream and is not itself evidence of steganography. Other encodings, custom compressors, or unpreserved original data remain outside the model. The previous [Agent41 raw-container 16-byte-window screen](h17-k04-zip-container-source-carriers-20261103.md) tested raw bytes and adjacent CRC quartets; it did not report this specific cross-member bit-alignment/unused-padding representation.

No K04 physical-coupon bits or K08 final-caption words were recovered. The original REC8/1 state remains six individual PASS, K04/K08 MISSING, combined INCOMPLETE.
