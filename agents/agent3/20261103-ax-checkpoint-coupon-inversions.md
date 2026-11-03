# 3 Nov 2026: AX transfer checkpoints as encoded complete K04 coupon (new hypothesis)

**Agent 3, ~20:12 UTC.** This exploratory mechanism interprets the eight two-byte CHUNK checkpoints of an original AX transfer as a *per-pair checksum chain of the 16-byte north coupon*. The route says K04 is opaque, so this channel is hypothetical; no original source connects an AX checkpoint with the selected ESC-N physical coupon. Distinct from CRC16-of-MT-output donor-stage probes, this directly *inverts eight observed 16-bit values into an entire proposed sixteen-byte coupon* before comparing the unchanged original K04 commitment.

Source: original `resources/evidence/transfers/transfer-audit.jsonl`, SHA256 `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`. All four transfers, earliest/latest attempt per seq0..7, ascending/reversed seq and both checkpoint endian views. Each proposed 16-byte coupon is XORed with the unchanged K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C`; its 16-byte K04 result is compared by full SHA256 to the untouched original target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

| Exact inverse serializer family | Complete K04 comparisons | Distinct full coupon candidates | Original K04 hits |
| --- | ---: | ---: | ---: |
| CRC16-CCITT / ARC over independent 2-byte pairs or cumulative 2-byte prefixes; initial 0, FFFF, 1D0F; xorout 0/FFFF | 768 | 768 | 0 |
| CRC32 low16/high16 of independent pairs or cumulative prefixes; initial 0/FFFFFFFF; within-pair byte orientation both ways | 392 | 392 | 0 |
| Fletcher16 mod255, independent pairs or cumulative; state initial (0,0),(255,255),(1,0),(0,1) | 266 | 200 | 0 |
| **Total** | **1,426** | Family deduplicated | **0** |

CRC32 is inverted via its exact affine 128x128 GF(2) map, built by injecting each of 128 one-bit coupon impulses and eliminating output bits. Of 512 full CRC32 source-model assignments, 188 are inconsistent (all independent-pair low16 cases), 128 pair/high16 and 128 prefix/high16 observations determine unique complete coupons, and 68 prefix/low16 observations leave rank127 and thus two complete coupons. Source-induced identical candidates occur across models. CRC16 has bijective 16bit-two-byte maps for both polynomials, so each checksum exactly reconstructs its pair, compensating for cumulative state. Fletcher16 can invert both bytes algebraically from its (s1,s2) recurrence, enumerating its 0 vs 255 alias where necessary.

An actual 16-byte synthetic coupon `0123456789ABCDEF0011223344556677` was regenerated inside every one of the **16 CRC32**, **24 CRC16** and **16 Fletcher16** protocol-mode control families, including all rank-deficient inverse completions. Entire source file SHA was pinned before original checks. A read-only standard-library SFT is available as an invocation-local artifact, This is an informational method record; the full source-pinned SFT can be deposited separately. The test does **not** authenticate the hypothetical channel, historical printer/transfer relationship, or a single actual K04 bit; it rules out only these finite named checksum protocols as ways of turning the surviving AX checkpoints into K04. Other checksum algorithms or independent sources remain possible. Do not grow this family by arbitrary checksum-width, polynomial, salt or record reordering without a new source reason.

Status: original six component PASS, K04 and K08 MISSING, combined INCOMPLETE. Original evidence, verifier and candidate were unchanged.
