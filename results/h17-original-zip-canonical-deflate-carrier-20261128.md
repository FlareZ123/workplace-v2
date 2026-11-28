# H-17 export ZIP: in-use compressed-bit carrier ruled out for every permitted member

**Agent 9 · 28 November 2026 · original-export integrity and recovery-surface test. Not a K04/K08 recovery.**

## Distinct question

Earlier original-ZIP investigations ruled out unindexed gaps and unused bytes following deflate streams. They did **not** test whether apparently valid, in-use compressed bits were chosen from noncanonical but plaintext-equivalent DEFLATE encodings to carry additional archive material. An equivalent, nonstandard compressed representation can preserve every extracted source byte while storing separate information in deflate block/tree choices. This test examines that distinct carrier without reading or processing the protected PDF.

## Original-source execution

Read only the permitted (non-PDF) members of the original local `h17-archive-dump.zip`. For each, parse its local header to locate the **exact compressed bytes**, decompress the named member normally, and recompress the identical plaintext with stock raw-DEFLATE from Python's zlib at each level 1 through 9. Compare the complete compressed bitstream byte-for-byte, not merely the CRC or decompressed source. Separately count member comments, extra-field variants, and distinct timestamp classes. The protected PDF is skipped *before* accessing its payload; no rendering, extraction, parsing, decoding or searching of that file or its derivatives occurred.

The [source-safe reproducer](../agents/agent9/h17_zip_deflate_canonicality_sft.py) refuses original-archive execution on public CI and outputs aggregate counters only. Its source-free planted control constructs two **different valid compressed streams** for the same plaintext (ordinary level-6 raw deflate versus Huffman-only raw deflate), detects their difference, and confirms both decompress identically.

| Original permitted archive observable | Result |
| --- | ---: |
| Regular permitted files | **45** |
| Raw-DEFLATE compressed regular files | **45** |
| Exact byte-for-byte matches to stock zlib level-6 raw-DEFLATE recompression | **45 / 45** |
| Noncanonical members under that baseline | **0** |
| Nonempty per-file comments | **0** |
| ZIP archive-level comment bytes | **0** |
| Unique central-directory extra metadata patterns | **2** |
| Distinct stored time stamps | **2** |

All 45 members also match at least one other stock zlib level in some cases; **level 6 matches every one**. The sole two timestamp/extra variants are 05:12:14 versus 05:12:16, and their assignment is completely explained by file class: all twenty `evidence/mail/NN.eml` files have the later timestamp, and the other twenty-five permitted files have the earlier timestamp. Central-directory Unix UID/GID values and permissions are otherwise constant. The two uniform timestamp classes therefore offer no unconstrained per-file hidden bit assignments.

## Consequence and limits

The present ZIP is **not an evident custom-deflate or ZIP-metadata covert carrier** for missing selected coupon bytes or the final keeper wording. A hidden message dependent on deliberately nonstandard in-use Huffman trees/deflate blocks would require a compressed-stream mismatch; none exists across the 45 permitted members. The same is true for an ordinary ZIP file comment or per-entry variable comments: all are absent.

This does not exclude steganography inside the **decompressed content** itself, a secret independently encoded in ordinary canonical bytes chosen upstream, or any information in the excluded PDF; the test never inspects that file. It also cannot establish that a source-authored final caption exists anywhere in the current export. There is no new K04 coupon or K08 phrase; canonical six PASS, K04/K08 MISSING, combined REC8/1 INCOMPLETE.

Do not repeat arbitrary recompression-level or archive-header sweeps without a concrete original archive anomaly. Focus on a source-authored full selected-coupon producer or verbatim final-caption carrier.
