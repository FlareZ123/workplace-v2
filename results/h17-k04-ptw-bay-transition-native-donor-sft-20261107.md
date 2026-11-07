# K04: bounded PTW bay-transition donor test under +300/+304

**Status:** finite negative under the hypothetical p951 native-eight bridge. No K04 component recovered. Neither ST offset is authenticated.

## Question

The +304 ST↔PTW hypothesis maps four L-29/N tickets to singleton PTW seals in bays A/B/C/D, immediately before the special PTW-417 four-bay closeout. This creates two source-derived 16-byte blocks:

- predecessor singleton seals from PTW-398/410/403/416, in bay order A/B/C/D or field-sketch order B/D/A/C;
- current PTW-417 serials, in field-sketch order B/D/A/C or bay order A/B/C/D.

The competing +300 mapping supplies a different predecessor quartet from PTW-394/412/406/399. Test whether any of these old/current blocks, in the eight native p951 donor positions, reconstructs the committed K04 component.

## Method

Reused Agent49's source-pinned p951 basis (rank 15,365; selected row129 withheld) and Agent43's exact eight-native-word target projection at stages:

**328, 329, 330, 331, 724, 725, 726, 727.**

Constructed seven 16-byte donor blocks from original singleton PTW receipts and the latest signed/as-left PTW-417 serial for each bay:

| Donor block | Bytes |
|---|---|
| +300 predecessor, ticket order ST-094/ST-106/ST-099/ST-112 | 5C2B51169C4C4C9DF6C83ADF5AD7D397 |
| +300 predecessor, bay order A/B/C/D | 5C2B51165AD7D3979C4C4C9DF6C83ADF |
| +300 predecessor, field order B/D/A/C | 5AD7D397F6C83ADF5C2B51169C4C4C9D |
| +304 predecessor, ticket/bay order A/B/C/D | 0AEF4A08F8C5E995CCCCF4B80C814A5E |
| +304 predecessor, field order B/D/A/C | F8C5E9950C814A5E0AEF4A08CCCCF4B8 |
| PTW-417 current, field order B/D/A/C | D7DAD6BC9714519B7DAD0AD4BE8E87FD |
| PTW-417 current, bay order A/B/C/D | 7DAD0AD4D7DAD6BCBE8E87FD9714519B |

For every ordered pair of distinct blocks, each donor was independently interpreted using all eight combinations of little/big 32-bit byte order, forward/reversed word order, and native/inverse-tempered words. The resulting eight native words were passed through the p951 target projection; the route mask was applied and the official K04 SHA-256 commitment checked.

Total: **7 × 6 × 8 × 8 = 2,688** complete candidates.

## Result

**0 / 2,688 commitment matches.**

All 2,688 candidate components were distinct. No old/current PTW quartet pairing under either offset and the tested order/representation family matched the official K04 commitment.

## Scope

This is a bounded negative for these seven source-derived blocks, the two candidate ST offsets, the stated bay/ticket orders, and the eight donor interpretations. It does not establish that PTW serials are native MT words, prove either offset, or exclude a different source field, arbitrary bay permutation, different transition function, or other historical producer. The +304 crosswalk remains a retrieval hypothesis only.

The result complements Agent43's earlier donor SFT: the present test adds the +300/+304 predecessor seal quartets, which were not in its donor list. Do not repeat this exact block-pair/serialization family without new source evidence.

## Reproduction

Run **python agents/agent12/ptw_bay_transition_native_donor_sft.py**. The script reads the original receipt, printer, route and acceptance files and performs no writes.
