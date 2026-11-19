# Independent review: K05 LOW-IF-EVEN side channel

**Agent20 | 19 November 2026 | independent source-pinned review**

## Decision

The K05 arithmetic in Agent35's reproducer is correct. The proposed alternate selector produces the published two-byte output `0A4D` under the pre-registered LOW-IF-EVEN interpretation. However, `0A4D` is **not unique to that selector**: two of the 16 possible per-latch masks produce it. The result therefore remains a conditional K08 side-channel observation, not independent validation of the selector, a general routing operator, or a workbook carrier.

The authoritative K05 reducer remains unchanged and passes its original slot commitment.

## Frozen cue versus inferred mapping

The preceding source-local note analysis derives the string `LOWIF` from the selected note-count sequence and obtains `EVEN` from the first word of N11. I treated the resulting phrase **LOW IF EVEN** as pre-registered for this review.

The semantic application is a separate inference:

- `LOW` is interpreted as choosing the lower of the two valid sequence values;
- `EVEN` is interpreted as the parity of the latch ordinal 0..3;
- the resulting mask is low/high/low/high, decimal mask 10.

No K05 source record says to use that alternate selection. The explicit K05 route and recorder-format note instead require the greatest CRC-valid sequence per latch. The alternate rule is therefore evaluated only as a possible K08 side channel, never as K05 recovery.

## Independent source parse

The reproducer independently parses the original 88-record TRP2 file, verifies CRC32, applies the published node/event/time window, and preserves the four-byte control words as stored.

Pinned sources:

| Source | SHA-256 |
|---|---|
| `trip-recorder.raw` | `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba` |
| `format-note.txt` | `78ff213040de20f81bc582cdfc25a4d0930ceb2d3956dbcc944b775b88fd7b22` |
| `mail/10.eml` | `ccfc592fe570ca6928a74de813c378443030e841bba169434c0f413721122e48` |
| `recovery-routing.json` | `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5` |

There are 12 raw rows in the K05 window: eight CRC-valid rows (two per latch) and four CRC-invalid later rows (sequences 900–903). The invalid rows must be excluded under both the format note and MAIL-10.

| Latch | Valid lower sequence | Valid higher sequence | Invalid later sequence |
|---:|---|---|---:|
| 0 | 200 `42BFD053` | 300 `FF8B7820` | 900 |
| 1 | 201 `8052760C` | 301 `0A56E858` | 901 |
| 2 | 202 `6FC2B743` | 302 `6DCDA00E` | 902 |
| 3 | 203 `BFB00270` | 303 `F01E4572` | 903 |

## Exhaustive 16-mask result

Bit 0 of a mask selects the higher sequence for latch 0; bit 1 does so for latch 1, and so on. The same established byte-LSB / first-bit-as-LSB packer is applied to each resulting 16-byte string.

| Mask | Selected sequences (latch 0..3) | Packed bytes |
|---:|---|---|
| 0 | 200, 201, 202, 203 | `0A1D` |
| 1 | 300, 201, 202, 203 | `031D` |
| 2 | 200, 301, 202, 203 | `0A1D` |
| 3 | 300, 301, 202, 203 | `031D` |
| 4 | 200, 201, 302, 203 | `0A13` |
| 5 | 300, 201, 302, 203 | `0313` |
| 6 | 200, 301, 302, 203 | `0A13` |
| 7 | 300, 301, 302, 203 | `0313` |
| 8 | 200, 201, 202, 303 | `0A4D` |
| 9 | 300, 201, 202, 303 | `034D` |
| **10** | **200, 301, 202, 303** | **`0A4D`** |
| 11 | 300, 301, 202, 303 | `034D` |
| 12 | 200, 201, 302, 303 | `0A43` |
| 13 | 300, 201, 302, 303 | `0343` |
| 14 | 200, 301, 302, 303 | `0A43` |
| **15** | **300, 301, 302, 303** | **`0343`** |

There are eight distinct packed outputs. The apparent `0A4D` / M10 match occurs for **both masks 8 and 10**, not just the pre-registered mask 10. The reason is exact: latch 1's two valid control words, `8052760C` and `0A56E858`, both have byte-LSB vector `0000`. Changing that latch's selection cannot change the packed result.

The official all-high mask 15 yields the accepted K05 component:

`FF8B78200A56E8586DCDA00EF01E4572`

Its SHA-256 matches the unchanged K05 slot commitment. Its low-bit output is `0343`, not `0A4D`. The alternate mask-10 raw string does not match the K05 commitment, as expected for a separate side-channel construction.

## Negative and control comparisons

- All-low mask 0 gives `0A1D`.
- Opposite parity (high/low/high/low), mask 5, gives `0313`.
- Incorrectly allowing the CRC-invalid latest rows 900–903 gives `6428`; this violates the explicit CRC rule.
- Reversing the within-byte bit-packing direction for mask 10 gives `50B2`, not `0A4D`.

These are finite controls, not calibrated probabilities. The two-of-sixteen result is an exact combinatorial ambiguity for this carrier, not a statistical p-value.

## Follow-on boundary

I did not extend LOW-IF-EVEN to K03. The signed CLOSED/AS_LEFT K03 records do not form four clean two-row revision pairs: bay A has three eligible records (two distinct revision-1 rows and one revision-2 row). Applying the same four-position selector would require an arbitrary tie-break. K02's even/odd revision pilot is already recorded by Agent35, and K07's transfer attempts have an explicit source-defined greatest-attempt/attempt-2 rule.

**Research consequence:** preserve `0A4D` as a conditional low-bit consistency observation, but do not use it to justify further retry/revision sweeps, cell/page/mail reinterpretations, or a workbook claim. A new extension needs a source rule that uniquely selects its alternatives or a prospective external discriminator. No K08 commitment, candidate phrase, canonical candidate, verifier, acceptance file, or original evidence was used or changed.

## Reproducer

`agents/agent20/k08_k05_low_even_independent_review.py`

Run from the repository root:

```sh
python agents/agent20/k08_k05_low_even_independent_review.py
```

The script pins the original TRP2, format note, MAIL-10, route, and acceptance files; enumerates all 16 masks; checks the official K05 reducer against its unchanged commitment; and prints the controls above.
