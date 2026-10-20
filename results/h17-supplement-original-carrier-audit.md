# H-17 supplementary office corpus: finite literal-carrier audit

**Agent 10 | 20 October 2026, UTC.** Original six-slot state remains **six PASS, K04/K08 MISSING, combined INCOMPLETE**. This report excludes only precisely defined literal-source carriers; it does **not** recover an authentic coupon or a single final-caption word.

## Distinct source question

The predecessor's [all-file original-member audit](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-all-file-carrier-bound.md) scanned the **earlier 43-member export** for direct K04/K08 components, masked K04 raw/hex coupon payloads, and exact K08 contiguous 1–40-word text. The 20 October supplement added four office members, including the separately decryptable BX25/08 property folio. Have any of those **later-added** members carried an accepted literal K04 or K08 value, including in the PDF's decoded content? The previous property-identity/PDF review already inspected the visible folio and annotations, but was not an exhaustive masked 16-byte window and K08 HMAC span sweep over these added bytes.

## Read-only method and exact scope

Source is the attached **50,526-byte** export, ZIP SHA-256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`, which [exactly matches current repository original evidence](h17-attached-zip-integrity.md). Script: [`work/h17_supplement_carrier_audit.py`](../work/h17_supplement_carrier_audit.py), Git blob `b58edb632237bfb2bc0c06811fbb4972003a94a3`. Local Python 3, `pypdf 5.9.0`, original `acceptance.json` and `recovery-routing.json` read-only. PDF original is encrypted and is opened solely with the previously established authorized numeric release code `8131`.

For each original supplement member and two **separately counted derived PDF views** (decrypted page content stream and extracted page text), check:

1. Every sliding **16-byte raw window**, SHA256 both raw bytes as a direct K04/K08 candidate and the bytes XOR the original K04 mask as a candidate for original K04.
2. Every sliding 32-nibble window inside each contiguous 32+ ASCII-hex run, with both direct and K04 mask-XOR comparisons.
3. Every **contiguous 1–40-word span** of source text decoded as UTF-8 with replacement, after original K08 ASCII lowercase/whitespace normalization, HMAC-SHA256 under the original desk nonce, first 16 bytes, and original full K08 SHA256 commitment.

These are **candidate assignments**, with duplicates across windows and PDF views. An encrypted raw PDF produces many arbitrary decoding/normalization spans, but the test still covers that defined representation. Derived PDF content is not an independently sourced historical record.

Positive controls **PASS**: an embedded source-known retained ACK payload was found by the byte/mask checker against a synthetic *in-memory* target, and Emily's exact N06 known draft is rediscovered from source-normalized HMAC under a synthetic in-memory target. Neither test changes original commitments. All original bytes remained unchanged.

| Source/view | SHA-256 of byte stream | Raw windows | Hex windows | K08 spans | Original commitment hits |
|---|---|---:|---:|---:|---:|
| Original `BX25-08.pdf` | `b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425` | 5,392 | 460 | 31,860 | 0 |
| Original fleet return note | `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf` | 1,375 | 0 | 8,180 | 0 |
| Original retired bookmark list | `b9261ac17524e66bb5a6e3f3ce4996df65737aa34564b6d29a87ebab681a6096` | 2,484 | 0 | 15,100 | 0 |
| Original supplier reconciliation | `73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e` | 1,592 | 0 | 13,620 | 0 |
| Derived PDF decrypted content stream | `09e581fcbc2cc8afeb6738ba6a9577fe2bbc12158fd778a74339b7640586d207` | 3,100 | 188 | 30,060 | 0 |
| Derived PDF extracted page text | `294f9f76c949a5daed7647643b3abf11d82639ef05e4f510f5c78db3e19084f5` | 984 | 0 | 4,980 | 0 |
| **All six views** | | **14,927** | **648** | **103,800** | **0** |

Original four-file-only counts: 10,843 raw byte windows, 460 decoded hex windows, 68,760 K08 word spans. Derived PDF views add 4,084, 188 and 35,040 assignments respectively. Script output is deterministic for the specified PDF parser and local original bytes.

## Meaning and remaining evidence gap

The supplement contains **no original-commitment-accepted K04 or K08 value** in the tested literal carrier classes, whether as an entire raw or ASCII-hex 16-byte value or as a normalized 1–40-word contiguous caption in the tested representations. This is an incremental post-supplement audit, complementary to the predecessor's much larger pre-supplement scan and earlier visual/object inspection. It does not exclude unobserved physical media, an image requiring different decoding, noncontiguous text construction, longer text, arbitrary external correspondence, a corrected mask, or a damaged spool reconstruction. Search counts measure coverage of a **defined extraction model**, not information about the unknown 128-bit K04 value.

The specifically identified source requirements remain an independently authenticated original `ESC-N / PS-261003-0417` **ACK RECOVER attempt 2** coupon/mask/checksum and the **verbatim final** Emily keeper-margin wording. The source [intake issue](https://github.com/FlareZ123/workplace-v2/issues/1) and [new-witness checker](h17-original-witness-intake-gate.md) already specify how to validate them. No material change to `candidate.json` or the official verifier is warranted.
