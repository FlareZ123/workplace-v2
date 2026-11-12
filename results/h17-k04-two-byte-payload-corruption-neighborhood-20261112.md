# K04 selected ACK2: arbitrary two-byte copy-corruption neighborhood

**Agent 43 — 12 November 2026.** Source-pinned exact candidate search. No K04 component recovered.

## Question

The selected retained-fragment payload for PS-261003-0417 attempt 2 begins with the unusual repeated byte pair `A9A9`. Could that pair be an export fill/placeholder, or could the copied ACK2 packet otherwise differ from the physical coupon in only one or two byte positions? This is a bounded copy-integrity hypothesis, not an assumption that `A9A9` is a documented marker.

## Original source and selector

The unchanged route selects the last acknowledged `RECOVER` attempt for exact job `PS-261003-0417`; its retained ACK2 payload is:

```
A9A9DC5731A5E2AE879C47215C2559D5
```

The route reduction is unchanged: physical coupon XOR `8556C8CB6140A7F9A5123AC7571BEE1C`, then SHA-256 against the original K04 commitment.

Source SHA-256 pins:

- spool: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- routing: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- acceptance: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

The export contains 133 16-byte payload fields. `A9A9` occurs as a prefix exactly once and as an adjacent pair anywhere in a payload exactly once: the selected ACK2. This is an observed anomaly, not evidence of what the original bytes were.

## Exact candidate construction

The SFT `agents/agent43/k04_two_byte_payload_corruption_sft.py` uses only the Python standard library and reads original resources without modifying them.

1. Replace the first two bytes exhaustively (`2^16 = 65,536` candidates), leaving the other fourteen bytes copied.
2. Enumerate every pair of byte positions among the sixteen (`C(16,2)=120`); try all `256^2` values at each pair. This covers every packet at Hamming distance zero, one or two from the retained ACK2 payload: **7,864,320 assignments**. For each complete 16-byte candidate, apply the original XOR mask and the full original SHA-256 commitment.
3. Run the same official reduction against a planted two-byte synthetic correction at positions 3 and 14. The test must recover that candidate uniquely.

## Result

| Test | Complete assignments | Original K04 hits |
|---|---:|---:|
| First-two-byte replacement | 65,536 | **0** |
| Any two byte positions, arbitrary replacement values | 7,864,320 | **0** |

The synthetic positive recovered the planted `1234` replacement at positions 3 and 14 with exactly one hit.

**Conclusion:** no accepted physical coupon lies at Hamming distance 0, 1, or 2 from the retained ACK2 payload under the original K04 mask and commitment. If the selected ACK copy is wrong, a valid physical coupon differs in at least three byte positions, or the relationship is not a direct same-position byte copy.

## Limits and next action

The result does not authenticate or discredit the ACK2 media, establish that `A9A9` is a sentinel, test three-or-more-byte corruption, or rule out a different copy-stage transform. The custodian note explicitly warns that an ACK proves receipt rather than payload correctness; the retained-fragment export is not an integrity witness.

Do not repeat the two-byte neighborhood or prefix search. A meaningful next advance requires an independently sourced attempt-2 request/native `.SPL/.SHD` object, a physical coupon/rendered output with an integrity link, or a genuinely different source-supported complete-candidate mechanism.

The script pins the three original source files, checks the exact job/attempt selector and all candidate counts, and includes the planted positive. Original evidence, route, acceptance commitments, candidate and verifier were not changed.
