# K04 selected PS-0417 ACK2 bit-error neighborhood screen

**Agent 1 · 21 November 2026 · bounded source-specific candidate search · no K04 bits recovered**

## Question

MAIL-16 warns that the retained printer payload has no independent payload checksum for every recovered line. The route nevertheless selects the last acknowledged RECOVER payload for exact job PS-261003-0417 and XORs it with the K04 mask. Could a small number of bit errors in that selected 16-byte payload explain why the direct candidate fails the K04 commitment?

## Exact candidate and method

The script pins the original spool, routing, and acceptance SHA-256 values. It selects only PS-261003-0417 / attempt 2 / ACK / RECOVER, obtains the 16-byte payload, and applies the published K04 mask exactly as the route specifies.

The direct component candidate is:

- Selected payload: A9A9DC5731A5E2AE879C47215C2559D5
- K04 mask: 8556C8CB6140A7F9A5123AC7571BEE1C
- Direct component: 2CFF149C50E54557228E7DE60B3EB7C9
- K04 commitment: 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0

The direct candidate does not match. The search then exhaustively tests every distinct bit-flip pattern of Hamming weight 1, 2, 3, or 4 across the 128-bit component. Because XOR with a fixed mask preserves bit differences, this is equivalent to the same bit-error neighborhood in the selected payload.

| Hamming weight | Candidates tested |
|---:|---:|
| 1 | 128 |
| 2 | 8,128 |
| 3 | 341,376 |
| 4 | 10,668,000 |
| **Total** | **11,017,632** |

The local run completed in 14.57 seconds. No candidate matched the K04 commitment at any radius.

## Interpretation and limits

This closes the small bit-error model through four flipped bits. It is a useful extension beyond the earlier two-byte-support search: the present search includes patterns spread across three or four byte positions, which were not covered by that support restriction.

It does **not** establish that the retained ACK2 payload is authentic, and it does not exclude three-or-more-byte arbitrary substitutions, larger corruption, a wrong route selection, or a missing native spool/media source. It does not justify treating the unverified payload as the original coupon.

**Recovery status unchanged:** K01/K02/K03/K05/K06/K07 accepted; K04 and K08 remain missing; combined REC8/1 acceptance remains incomplete.

## Reproducer

[agents/agent1/k04_ack2_bit_hamming_radius4_sft.py](../agents/agent1/k04_ack2_bit_hamming_radius4_sft.py) verifies source hashes, selects the exact ACK2 row, and repeats the complete radius-1–4 search without modifying source files.