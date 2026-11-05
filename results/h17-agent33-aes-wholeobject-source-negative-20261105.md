# K04/K08 source-wide AES full-object carrier experiment

**Agent 33, 5 November 2026.** Exploratory original-target negative, conditional on an unverified AES reconstruction model. No historical record identifies AES as the printer/caption encoding or says that the eight tested original source values are its key.

## Hypothesis and source

A source member might contain a complete encrypted coupon or literal final caption. The test reads all evidence file bytes and long ASCII-hex strings from the untouched original 46-member ZIP: 51 source streams, 112,756 bytes, each scanned at every 16-byte window.

Original source SHA-256s: crew notes 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb; spool 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. Keys: the six individually accepted K01/K02/K03/K05/K06/K07 bytes, the official K04 route mask and K08 desk nonce, eight distinct 16-byte AES keys.

For each 16-byte source window, calculate AES-ECB encrypt/decrypt and AES-CBC decrypt using zero, mask, nonce and preceding-source-block IVs (the latter only where defined). Hash each resulting complete 16-byte candidate both directly and XORed with the unchanged route mask to check the original **full SHA256** K04 commitment. Attempt K08 HMAC16 reduction only on entirely printable 16-byte plaintexts, or complete printable text with valid PKCS#7 or NUL padding. Compare against the original **full SHA256** K08 commitment.

## Executed full-original results

| Mechanism | Candidate blocks | Source-supported complete hits |
| --- | ---: | ---: |
| ECB encrypt | 895,928 | 0 |
| ECB decrypt | 895,928 | 0 |
| CBC decrypt, up to four IV choices | 3,577,184 | 0 |
| Direct and XOR-route K04 component tests | **10,738,080** | **0** |
| Complete readable K08 plaintext candidates | **0** | **0** |

Synthetic original-known Emily N02 HMAC16 matched BF889359B0303F2B2B2FD96AE841210B. Planted ECB coupon and 48-byte CBC phrase cryptographic roundtrips passed. The independent locally executed longer implementation SHA256 was f73824fad62f1e56e837a41c03f65efd6ac834ea66d90e5a76fc92e6bfb33951. Repo reproducer: [agent33/h17_aes_source_carrier_sft.py](../agents/agent33/h17_aes_source_carrier_sft.py). It pins the original sources and asserts all exact counts.

## Boundary

This excludes only a narrow **source-embedded complete ciphertext with one of eight source-contained AES-128 keys** interpretation, not other encryption keys, modes, longer encoded text without printable 16-byte segments, noncontiguous data, or absent originals. Source files, canonical candidate, route and verifier were not edited. K04 has zero independently authenticated selected physical coupon bits; K08 has no author-final word. Six individual PASS; combined REC8 incomplete.

Do not extrapolate the negative into an AES-independent nonexistence claim or relaunch an arbitrary secret-key dictionary. The next useful attack needs a different source-to-target transform or an actual original transport witness.
