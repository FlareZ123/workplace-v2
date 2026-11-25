# K04: reverse-Alea screen from the late PS-0417 REQUESTED event

**Date:** 2026-11-25  
**Status:** Bounded negative; no K04 candidate recovered  
**Reproduction:** `agents/agent16/k04_alea_reverse_late_request_sft.py`

## Question

The earlier seed-free Alea/MWC3 work found 8 of 384 word-order/per-word-endian views of the PS-0417 attempt-3 REQUESTED payload satisfying the necessary 21-bit carry condition. Its forward missing-middle test began from attempt 1, which had no valid views. This screen tests the reverse direction: can attempt 3 be inverted to recover the preceding four-word packet and satisfy the K04 commitment?

Two source-motivated packet distances were checked:

1. **One packet back:** attempt 3 follows the attempt-2 payload, with no separate generator output for the ACK dispatch event.
2. **Two packets back:** the missing attempt-2 REQUESTED body is followed by a separate ACK2 event before attempt 3.

The second case is conditional. MAIL-16 identifies attempt 3 as a button press that never returned an acknowledgement; the retained export does not establish that its payload is an authenticated printer output or whether ACK2 consumes a separate generator output.

## Method

- Pin the retained spool, route, and acceptance files by SHA-256.
- Identify the selected attempt-2 ACK row by metadata only. Its payload is not parsed into the candidate path.
- Enumerate all (4! \times 2^4 = 384) permutations of the four 32-bit words and independent per-word endian choices for the later attempt-3 REQUESTED payload.
- For each view, apply the exact inverse of the lag-3 multiply-with-carry recurrence with multiplier (2{,}091{,}639). The recurrence gives a necessary carry bound; quotient/remainder inversion recovers the preceding four-word packet. A forward replay must reproduce the observed late packet.
- Apply the inverse a second time for the explicit missing-request/separate-ACK alternative.
- For each recovered 16-byte predecessor, apply the routed K04 mask and test the full K04 SHA-256 commitment. Candidate bytes and candidate hashes are never printed or written.

A deterministic synthetic positive control recovers two planted preceding packets and passes the synthetic mask/commitment check.

## Result

| Check | Result |
|---|---:|
| Attempt-3 serializer views | 384 |
| One packet back: valid inverse/replay views | 8 |
| One packet back: distinct 16-byte packets / K04 hits | 8 / **0** |
| Two packets back: valid inverse/replay views | 8 |
| Two packets back: distinct 16-byte packets / K04 hits | 8 / **0** |
| Synthetic two-step reverse and commitment control | PASS |

## Interpretation and limits

Both specific predecessor hypotheses fail the unchanged K04 commitment. This closes only the one-packet and two-packet reverse-Alea constructions. It does not establish that the printer used Alea/MWC3, that REQUESTED3 was emitted by the same producer, or that ACK2 and REQUESTED3 were adjacent in the original queue. The ACK2 payload remains unverified dispatch-log material; no historical media-integrity conclusion follows from this test.

Do not expand this into further seed, phase, serializer, or arbitrary packet-offset sweeps. A native PS-0417 queue/job image or an authenticated request/ACK binding is still required to establish the historical producer and event sequence.

No candidate, acceptance, routing, verifier, or source evidence was changed.
