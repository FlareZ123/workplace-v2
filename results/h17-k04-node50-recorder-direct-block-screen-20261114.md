# K04 TRP2 node50 direct 16-byte donor screen

**Status:** bounded negative; no K04 bytes recovered.

## Question

Could the CRC-valid, source-indexed node50 recorder stream directly supply the K04 16-byte coupon payload under the declared XOR mask?

## Frozen source construction

Pinned inputs:
- `trip-recorder.raw` SHA-256: `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`
- `recovery-routing.json` SHA-256: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- `acceptance.json` SHA-256: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

The TRP2 dump has 88 records. Exactly 72 CRC-valid node50 records have sequence numbers 0–71. Before loading the K04 mask or commitment, the script constructs every 16-byte block in four record-defined families:

| Family | Construction | Candidates |
|---|---|---:|
| Four control words | Four consecutive raw 4-byte control fields | 69 |
| Four auxiliary words | Four consecutive 32-bit auxiliary fields in TRP2 little-endian encoding | 69 |
| Two control/aux records | Two adjacent records, each `control || aux` | 71 |
| Two aux/control records | Two adjacent records, each `aux || control` | 71 |
| **Total** | | **280** |

All 280 blocks are unique. For each block (b), the declared route is applied as (c=b\oplus mask), then SHA-256((c)) is checked against the K04 slot commitment.

## Result

- Candidate blocks: **280**
- K04 commitment hits: **0**
- New K04 bits recovered: **0**
- Synthetic positive control: **passed**

## Interpretation and boundary

None of these direct, record-aligned node50 blocks is the K04 payload under the declared mask. This does **not** establish that node50 is a printer-output source; no source-authenticated bridge from the node50 stream to PS-0417 has been identified. It also does not test a two-gap stage model or arbitrary transformations.

The node50 sequence-bridge work remains a separate negative. Do not treat this result as evidence that node50 records are printer output, and do not expand it into generic PRNG or byte-permutation searches. A further use of this stream requires a source-backed mapping to the missing printer-output blocks.
