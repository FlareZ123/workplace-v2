# K04: North ticket serial tuple and per-bay delta test

**Status:** bounded negative. No K04 component recovered.

## Question

Could the 16-byte K04 coupon be a direct four-serial tuple from the four North L-29/N predecessor seals, or the per-bay bytewise XOR delta between those predecessor seals and the current PTW-417 seals?

This is a source-derived candidate family. The five North binder tabs are explicitly ordered in `resources/evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt`; the two competing ST-to-PTW offsets (+300 and +304) are retained as hypotheses. The test does not assume either offset is authoritative.

## Source mapping

The North tabs are ST-094, ST-081, ST-106, ST-099, ST-112. The local signed CLOSED AS_LEFT receipts yield:

| Offset | Ticket order | Resulting bays | Missing receipt |
|---|---|---|---|
| +300 | PTW-394, PTW-381, PTW-406, PTW-399, PTW-412 | A, C, D, B | ST-081 → PTW-381 |
| +304 | PTW-398, PTW-385, PTW-410, PTW-403, PTW-416 | A, B, C, D | ST-081 → PTW-385 |

The +304 mapping produces A/B/C/D in North tab order. The +300 mapping produces A/C/D/B. This is only a property of the local receipts and the proposed offsets; it does not authenticate the mapping.

For the delta candidates, the current PTW-417 values are the latest signed CLOSED AS_LEFT serials by bay:
- A: `7DAD0AD4`
- B: `D7DAD6BC`
- C: `BE8E87FD`
- D: `9714519B`

The source-defined field order B/D/A/C comes from the PTW-417 closeout email.

## Candidate construction

For each offset, the test formed:
1. the four predecessor serials in North ticket order;
2. the same serials in bay order A/B/C/D;
3. the same serials in field order B/D/A/C;
4. the per-bay XOR delta against PTW-417, concatenated in A/B/C/D order;
5. the same delta in B/D/A/C order.

The direct predecessor blocks were:

| Candidate | 16-byte block |
|---|---|
| +300 ticket order | `5C2B51169C4C4C9DF6C83ADF5AD7D397` |
| +300 bay order A/B/C/D | `5C2B51165AD7D3979C4C4C9DF6C83ADF` |
| +300 field order B/D/A/C | `5AD7D397F6C83ADF5C2B51169C4C4C9D` |
| +304 ticket/bay order A/B/C/D | `0AEF4A08F8C5E995CCCCF4B80C814A5E` |
| +304 field order B/D/A/C | `F8C5E9950C814A5E0AEF4A08CCCCF4B8` |

The per-bay delta blocks were:

| Candidate | 16-byte block |
|---|---|
| +300 delta A/B/C/D | `21865BC28D0D052B22C2CB6061DC6B44` |
| +300 delta B/D/A/C | `8D0D052B61DC6B4421865BC222C2CB60` |
| +304 delta A/B/C/D | `774240DC2F1F3F29724273459B951BC5` |
| +304 delta B/D/A/C | `2F1F3F299B951BC5774240DC72427345` |

Each of the nine unique 16-byte blocks was tested in both natural K04 interpretations:
- block is already the component;
- block is the RECOVER payload, so XOR it with the recorded mask `8556C8CB6140A7F9A5123AC7571BEE1C`.

Each resulting 16-byte candidate was SHA-256 checked against the official K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Result

**0 / 18 commitment matches.**

The exact candidates and their hashes are printed by the reproducible script:
`agents/agent6/k04_north_ticket_serial_coupon_sft.py`.

This complements the earlier PTW bay-transition native-donor test. That work treated predecessor/current PTW blocks as possible native PRNG words; this test checks the serial tuples and the bay-aligned XOR deltas directly as the K04 component or pre-mask payload.

## Interpretation and limits

- The obvious four-serial predecessor tuple is not the K04 component under either tested offset/order.
- The same tuple is not the pre-mask payload under the documented XOR rule.
- The bay-aligned predecessor/current serial delta is also excluded for both offsets and both source-defined orders.
- The result does not validate +300 or +304, and it does not rule out a different source field or a different physical copy stage.
- Do not repeat this direct tuple/delta family without new source evidence.

The useful next direction remains recovery of the native ESC-N print object and its copy provenance: the original supplier commissioning note, the September cassette/asset records, the device-local job image or original print medium, and the physical coupon if retained. The PTW serial crosswalk should remain a locator hypothesis rather than a substitute for that evidence.
