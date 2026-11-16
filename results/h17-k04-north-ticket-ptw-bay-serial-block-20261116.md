# K04 candidate test: North ticket → PTW → bay-serial block

**Status:** bounded negative; do not promote as a K04 recovery.

## Hypothesis

The North return-register tickets may map to PTW permit IDs by adding 304 to the numeric ticket suffix. This is a candidate locator relation, not an authenticated foreign key. Applying it to the L-29/N tab sequence gives:

| Tab | Ticket | Candidate permit | Retained signed CLOSED / AS_LEFT record |
|---:|---|---|---|
| 01 | ST-094 | PTW-398 | Bay A, SG-0AEF4A08 |
| 02 | ST-081 | PTW-385 | No retained qualifying serial |
| 03 | ST-106 | PTW-410 | Bay B, SG-F8C5E995 |
| 04 | ST-099 | PTW-403 | Bay C, SG-CCCCF4B8 |
| 05 | ST-112 | PTW-416 | Bay D, SG-0C814A5E |

Under this candidate mapping, the four available receipts form one 4-byte serial per bay (A/B/C/D). That yields a candidate 16-byte block, distinct from PTW-417's K03 quartet; it does not authenticate the ST→PTW mapping.

## Test

The reproducible script is `work/h17_k04_north_ticket_ptw_bay_block.py`. It extracts the ticket tab order, applies the candidate +304 mapping, selects the latest signed CLOSED/AS_LEFT receipt per permit, and tests:

- The four serials in available L-29/N tab order (A/B/C/D).
- The same four serials in the signed PTW-417 witness-walk order (B/D/A/C), read from MAIL-04.
- The natural A/B/C/D order is the same as the available tab order and is not counted separately.
- For each order: direct 16-byte block and block XOR the K04 route mask.
- A bounded per-serial CRC32 block using serial bytes, serial ASCII, or permit/bay/serial ASCII; both endian encodings; direct and route-mask-XOR outputs.

There were 28 distinct candidates (two distinct orders × fourteen constructions per order). **No candidate matched** the K04 commitment:

`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The natural/tab-order raw block is `0AEF4A08F8C5E995CCCCF4B80C814A5E`; after the route XOR it is `8FB982C399854E6C69DECE7F5B9AA442`, whose SHA-256 is `468d6493a22a93b667b8b2f77bf21103a4b650316be3ebf604e738ff0d1fb938`.

## Interpretation and limits

This result establishes a useful source relationship among four L-29/N tickets and four retained PTW receipts, but **does not establish that the printer coupon is a serialization of those seal serials**. The ST→PTW +304 rule remains a locator hypothesis; ST-081→PTW-385 is absent from the retained qualifying receipts. The shared 417 suffix and the four-bay shape are not sufficient evidence to substitute these serials for the selected PS-0417 payload.

No verifier, acceptance commitment, or existing candidate was changed. The full 28-candidate output and source hashes are reproducible from the script. The K04 slot remains unresolved.

## Source hashes

| File | SHA-256 |
|---|---|
| print-fleet-retirement-note.txt | `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf` |
| supplier-reconciliation-L29.csv | `73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e` |
| seal-receipts.jsonl | `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32` |
| work-order-417.html | `158399fb294a647fc0ba7037af5f9fea9ba980c9034298770c209d13ea0cc88f` |
| 04.eml | `c9e83a610f9240c3abd4b4d435588bd9056de34edf6fa3e6d7aca88d8a21f439` |
| archive-labels.ini | `146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad` |
| recovery-routing.json | `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5` |
