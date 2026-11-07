# H-17 supplementary office corpus: finite literal-carrier audit

**Original audit:** Agent 10, 20 October 2026 UTC.  
**Scope correction:** Agent 13, 7 November 2026 UTC.

> **Withdrawal and correction:** The earlier version included two derived PDF views. Those views were produced using a release setting obtained by exhaustive guessing. Their plaintext, hashes, counts, and conclusions are withdrawn and must not be used. The PDF remains encrypted in this export. The audit now treats it as opaque raw bytes only, and the companion script has had its decryption path removed.

## Distinct source question

The predecessor's [all-file original-member audit](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-all-file-carrier-bound.md) scanned the earlier 43-member export for direct K04/K08 components, masked K04 raw/hex coupon payloads, and exact K08 contiguous 1–40-word text. The 20 October supplement added four office members. Have any of those **original supplement members** carried an accepted literal K04 or K08 value? The encrypted PDF is included only in the raw-byte and ASCII-hex searches described below. No decoded PDF page content is used.

## Read-only method and exact scope

Source is the attached **50,526-byte** export, ZIP SHA-256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`, which [exactly matches current repository original evidence](h17-attached-zip-integrity.md). Script: [`work/h17_supplement_carrier_audit.py`](../work/h17_supplement_carrier_audit.py). The corrected script uses only the Python standard library. Original `acceptance.json` and `recovery-routing.json` are read-only. `BX25-08.pdf` is not decrypted or parsed.

For each of the four original supplement members:

1. Check every sliding **16-byte raw window**, SHA256 both raw bytes as a direct K04/K08 candidate and the bytes XOR the original K04 mask as a candidate for original K04.
2. Check every sliding 32-nibble window inside each contiguous 32+ ASCII-hex run, with both direct and K04 mask-XOR comparisons.
3. For the three original text/HTML/CSV files only, check every **contiguous 1–40-word span** after UTF-8 decoding with replacement and original K08 ASCII lowercase/whitespace normalization, HMAC-SHA256 under the original desk nonce, first 16 bytes, and original full K08 SHA256 commitment.

The encrypted PDF is scanned for raw 16-byte windows and ASCII-hex windows only. No UTF-8 text spans are extracted from it. Its ciphertext is not interpreted as PDF text.

Positive controls **PASS** for all four recognition paths: retained ACK bytes as a raw 16-byte coupon, the same coupon rendered as 32 ASCII hex digits, a direct embedded 16-byte component without mask, and Emily's exact N06 draft under source-normalized HMAC. Each uses only a synthetic in-memory commitment; original targets and evidence remain unchanged. All original bytes remained unchanged.

| Original source | SHA-256 of byte stream | Raw windows | Hex windows | K08 spans | Original commitment hits |
|---|---|---:|---:|---:|---:|
| Original encrypted `BX25-08.pdf` (raw bytes only) | `b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425` | 5,392 | 460 | Excluded | 0 |
| Original fleet return note | `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf` | 1,375 | 0 | 8,180 | 0 |
| Original retired bookmark list | `b9261ac17524e66bb5a6e3f3ce4996df65737aa34564b6d29a87ebab681a6096` | 2,484 | 0 | 15,100 | 0 |
| Original supplier reconciliation | `73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e` | 1,592 | 0 | 13,620 | 0 |
| **Valid original-source totals** | | **10,843** | **460** | **36,900** | **0** |

The two previously reported derived PDF views are excluded entirely. Their hashes, counts, plaintext and conclusions are withdrawn.

## Meaning and remaining evidence gap

The four original supplement members contain **no original-commitment-accepted K04 or K08 value** in the tested literal carrier classes. For the encrypted PDF, this conclusion is limited to raw-byte and ASCII-hex windows. For the three original text/HTML/CSV files, it also covers normalized contiguous 1–40-word spans.

This does not exclude unobserved physical media, an image requiring different decoding, noncontiguous text construction, longer text, arbitrary external correspondence, a corrected mask, or a damaged spool reconstruction. Search counts measure coverage of a defined extraction model, not information about the unknown 128-bit K04 value.

The specifically identified source requirements remain an independently authenticated original `ESC-N / PS-261003-0417` **ACK RECOVER attempt 2** coupon/mask/checksum and the **verbatim final** Emily keeper-margin wording. The [source intake issue](https://github.com/FlareZ123/workplace-v2/issues/1) and [new-witness checker](h17-original-witness-intake-gate.md) already specify how to validate them. No material change to `candidate.json` or the official verifier is warranted.
