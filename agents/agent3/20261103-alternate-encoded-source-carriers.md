# 3 Nov 2026: alternate textual encoding carrier hunt (K04)

**Agent 3 | original ZIP scan, original target unmatched.**

The inherited [v1 all-file original-carrier census](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-all-file-carrier-bound.md) already tested every exact 16-byte raw window and 32-character ASCII hex window against the original K04 XOR mask and immutable SHA256 commitment. It did **not** enumerate common textual transfer encodings. A printer coupon could theoretically have survived in a separate copied source as 16 encoded bytes, rather than as raw hex.

The [source-pinned single-file reproducer](k04_encoded_carrier_sft.py) inspects **all 46 regular members of the original supplied `h17-archive-dump.zip`**, file SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91e6c94e1d64342bf7` (original member-based source pin: spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`). Original unchanged K04 mask `8556C8CB6140A7F9A5123AC7571BEE1C`, target SHA256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

It scans ASCII-eligible runs in the original bytes, including binary file members via exact Latin-1 byte mapping, for 22/23/24/28/32-character standard and URL-safe base64 windows, 26/32-character base32, 21..24-character Bitcoin base58, and 20-character Python Base85/Adobe ASCII85. Decode, select every **complete 16-byte window** inside the decoded bytes, apply the original XOR mask, and compare **full SHA256**. A preselected synthetic 16-byte packet roundtrips through all except base58, whose leading-zero and nonzero decoding controls are separately tested.

Original complete assignments:
- base64-url: **39,572**
- base64-standard: **35,379**
- ascii85: **8,083**
- base85: **4,167**
- base58: **927**
- base32: **0**
- total: **88,128**, **zero original K04 matches**.

These counts include duplicate decoded buffers and overlapping encoded substrings. This closes a small *new carrier format*, not the case's substantive original payload gap. It cannot recover a segmented, encrypted, compressed, keyed, or missing paper coupon, and original source gives no reason to believe it used these ASCII encodings. The complete selected K04 value still has **0/128 independently authenticated bits**. K08 remains an unknown final authored sentence. Six original slots PASS, combined incomplete. No original evidence or target was modified.
