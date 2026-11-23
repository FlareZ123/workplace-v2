# Prime-field global erasure-code falsifier — 2026-11-23

## Question

Could the six accepted 16-byte components be six known evaluations of one degree-5 polynomial, with K04 and K08 as the two erasures? This is a cross-slot mechanism distinct from the previously reported GF(2^n) global RS(8,6) search.

The natural slot coordinates are K01=x1, K02=x2, K03=x3, K04=x4, K05=x5, K06=x6, K07=x7, K08=x8. The six inputs are the current accepted candidate values; no missing value was used as an input.

## Method

For each field, compute the unique degree-at-most-5 Lagrange interpolant through the six known points (1,2,3,5,6,7), then evaluate at x=4 and x=8. Compare SHA-256 of each 16-byte candidate with the immutable per-slot acceptance commitment.

Tested only these natural prime-field constructions:

1. **GF(257), byte-column representation:** each of the 16 byte positions is an independent degree-5 polynomial over the prime field GF(257), with byte values 0–255 mapped directly to field elements. Both output blocks remained in the byte range.
2. **128-bit-symbol field:** one 16-byte component is one field element in p=2^128+51 (verified prime; the first prime above 2^128). Tested both big-endian and little-endian interpretations of the 16-byte symbols.

No alternate x-coordinate, field search, coefficient search, or arbitrary permutation was performed.

## Results

### GF(257), 16 byte columns

| Missing slot | Interpolated 16-byte candidate | SHA-256 matches acceptance? |
|---|---|---|
| K04 | `75F86CAC15BBA3ACD27CBA5C88B9B63E` | No |
| K08 | `6A7E618E27C0CCF37938BD83049657D6` | No |

### p = 2^128 + 51, 128-bit symbols

| Interpretation | Missing slot | Interpolated candidate | SHA-256 matches acceptance? |
|---|---|---|---|
| Big-endian | K04 | `0F51DF9F157B16D278A2FA1CFBC5B637` | No |
| Big-endian | K08 | `6E3A99411C7D0AAEBBF8F84742C74DE2` | No |
| Little-endian | K04 | `949EF978D5FA2F862B567A9C95EC35A5` | No |
| Little-endian | K08 | `A4C21D86DAF48831357B7DBE4894C8CD` | No |

The official acceptance commitments tested were:

- K04: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`
- K08: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`

**Outcome: no K04 or K08 commitment hit.**

## Interpretation and limits

This falsifies these two simple prime-field constructions at the natural 1-based slot coordinates. It does not establish that every cross-slot relation is impossible, and it does not alter the existing source-defined derivations. The six accepted components, candidate file, acceptance file and verifier were not modified.

The test is reproducible from the six accepted values and the field definitions above; it requires no external source data.
