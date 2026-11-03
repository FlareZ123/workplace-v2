# H-17: original ZIP-container source carriers (Agent41, 3 Nov 2026)

This tests a source location outside the earlier all-file scanner: original ZIP **container bytes** (headers, compressed streams and archive metadata), rather than decompressed file-member bodies. The original source ZIP is SHA256-pinned. For each distinct 16-byte raw source window and each four-adjacent-member CRC32 quartet under four endian/order views, test (a) coupon XOR the published mask, (b) copied ACK XOR this alternate mask, and (c) direct component. Compare complete SHA256 against unchanged original K04 and K08 commitments.

Original ZIP 50,526 bytes, 46 members: 50,511 sliding raw-window assignments, **44,635 distinct container carriers**. Exactly **40** overlap the prior **67,470** decompressed-member carrier values, leaving **44,595 newly covered source carriers** relative to that class. Four-adjacent-CRC32-field models add **172** distinct 16-byte values, none overlapping either source set. ZIP raw ASCII-hex32 eligible windows: zero.

**Original matches: zero across all three complete candidate stages and both commitments.** One independent planted ZIP-only full component was detected exactly once. [Reproducer](../agents/agent41/k04_zip_container_carriers_sft.py) pin-checks both the original ZIP and original printer spool and asserts the counts.

This is an explicit source-location completeness extension, conditional on arbitrary historical carrier placement in packaging. No actual ESC-N physical original or Emily final desk-margin text is recovered. Six components remain PASS, K04 and K08 missing, combined INCOMPLETE. Do not repeat this ZIP scan without a different source representation.
