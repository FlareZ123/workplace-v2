# K08 LOW BIT partial specificity controls (19 November 2026)

**Status:** bounded component/transfer/print controls only. This is not the Critic-requested full end-to-end null benchmark, does not recover K08, and does not change any candidate or acceptance data.

Reproducer: [agents/agent9/k08_lowbit_partial_controls.py](../agents/agent9/k08_lowbit_partial_controls.py)

## Question

How selective are three currently used LOW BIT steps when the complete accepted-component set, all retained transfer retries, and the entire reconstructed print payload set are treated as controls?

## Pinned inputs and method

The standard-library script pins:

- `resources/acceptance.json`: SHA-256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`
- `resources/evidence/print/spool-reconstruction.log`: SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- `resources/evidence/transfers/transfer-audit.jsonl`: SHA-256 `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`
- `resources/evidence/recovery-routing.json`: SHA-256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`

The six populated candidate slots K01/K02/K03/K05/K06/K07 are each checked against their unchanged REC8/1 slot commitment before use.

The common selector is implemented literally: take each byte's least significant bit, pack the first byte as bit 0 (LSB-first), convert the packed bytes to uppercase hex, then apply the same character-LSB packing to that hex string. For a 16-byte input, the packed hex has four characters, so the final selector is necessarily in **0..15**. Therefore a random selector has a **15/16 = 93.75%** chance of landing on one of the existing note IDs N01–N15; N16–N24 are unreachable by this four-bit selector.

## Results

### 1. Accepted-component assignment control

The source-derived A / LOW / BIT selector positions are fixed at 1, 6, 2. All ordered assignments of three distinct values from the six accepted components were enumerated: (6P3=120).

| Measure | Result |
|---|---:|
| Ordered assignments | 120 |
| Exact case-insensitive YEA outputs | **1** |
| Assignment yielding YEA | K01, K06, K02 |
| Assignments yielding three ASCII letters | 24 |
| Selected lower-half output | `yEa` |
| Selected upper-half low-bit bytes | `04 83 F9` (non-printing) |

This is a positive **conditional** specificity result for the component bridge: given the already-derived selectors 1/6/2 and the lower-half/byte-LSB convention, the observed ordered component assignment is the only one of 120 that yields YEA. It is not a test of how selectively the preceding note/author process chose those selectors, and it does not validate the final keeper phrase.

### 2. Transfer retry-mask controls

Each retained transfer has eight chunks and two attempts per chunk. All (2^8=256) attempt-1/attempt-2 masks were enumerated for each transfer. Mask 255 is the source-required greatest-attempt-per-sequence vector.

| Transfer | Official mask | Official lowpack | Official selector | Masks reaching selector 11 | Masks yielding exact 53D5 |
|---|---:|---|---:|---:|---:|
| AX-7778 | 255 | 6A58 | 6 | 0/256 | 0/256 |
| AX-7781 | 255 | E188 | 3 | 72/256 | 0/256 |
| AX-7782 | 255 | 53D5 | 11 | 64/256 | 8/256 |
| AX-7783 | 255 | EF7B | 5 | 0/256 | 0/256 |

For AX-7782, the N11 endpoint occurs under **64/256 (25%)** possible retry masks. Exact 53D5 occurs under **8/256 (3.125%)**, including the official mask 255. AX-7781, a dry-run control, reaches selector 11 under 72/256 masks despite its official greatest-attempt vector selecting 3.

The source rule remains decisive: MAIL-13 and the K07 route require the greatest attempt per sequence, so only mask 255 is the committed K07 vector. The other masks are counterfactual controls, not valid K07 candidates. The previously discussed mixed even/odd mask 170 is not K07; on AX-7782 it produces 50D4, selector 1.

### 3. Full print-payload controls

All 133 retained 16-byte spool payloads were processed with the same selector.

| Measure | Result |
|---|---:|
| Payload rows | 133 |
| Rows mapping to N01–N15 | 122/133 (91.73%) |
| Uniform 4-bit expectation | 93.75% |
| Rows mapping to N05 | 13/133 |
| RECOVER rows mapping to N05 | 4 |

The selected PS-261003-0417 attempt-2 ACK/RECOVER payload maps to 3BED → 5 → N05 (“Boat deck”). That is not unique: the same-job attempt-1 REQUESTED row and two other RECOVER records also map to 5. Same-job attempt 3 maps to N01; ESC-S / PS-261003-0448 ACK maps to N07; the unrelated WATCH-SPARE / PS-261003-0420 attempt-2 ACK maps to N09, a surviving galley-board caption.

The selected K04 ACK is a dispatch-log payload, not a media-integrity witness. Its N05 mapping is a locator observation only; the high note-range base rate and the WATCH-SPARE control argue against counting it as independent evidence for either K04 or K08.

## Interpretation

The controls show two different things:

- The **component permutation** result is unusually selective conditional on the fixed A/LOW/BIT selectors and lower-half operation: one of 120 ordered accepted-component assignments produces YEA.
- The **note-selector endpoints** are much less selective when the whole source population is tested. The four-hex-character selector has only four bits; 15/16 outputs are valid note IDs. This is reflected empirically by 122/133 print payloads mapping to N01–N15. The K07-to-N11 endpoint also appears under many counterfactual retry masks.

These results must not be combined as independent probabilities: the pipeline reuses the same bit-packing operator at multiple stages, and the source-role restrictions differ by carrier. The official K07 vector remains source-fixed, while alternative retry masks are controls only.

## Limitations and next step

This reproducer does **not** implement the full frozen pipeline or the complete Critic-requested null design. It does not permute note authors/IDs, test all note/bookmark assignments, assess the physical-bookmark versus browser-bookmark link, or evaluate the complete N20/N23 text-selection path. Agent22 has been asked to publish the frozen end-to-end specification and include these controls. This partial result is supplied as a reusable control module, not a substitute.

No candidate, slot commitment, source record, or verifier was changed. No K04 coupon or K08 wording was recovered.
