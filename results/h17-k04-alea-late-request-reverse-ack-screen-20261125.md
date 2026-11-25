# K04: reverse-Alea screen from the late PS-0417 REQUESTED event

**Date:** 2026-11-25  
**Status:** Bounded negative; no K04 candidate recovered  
**Reproduction:** `agents/agent16/k04_alea_reverse_late_request_sft.py`

## Question

The earlier seed-free Alea/MWC3 work found 8 of 384 word-order/per-word-endian views of the PS-0417 attempt-3 REQUESTED payload satisfying the necessary 21-bit carry condition. Its forward missing-middle test began from attempt 1, which had no valid views. This screen tests a distinct direction: if attempt 3 is the next four-word Alea output block after the selected attempt-2 ACK, can the exact inverse recurrence recover the preceding four-word block and satisfy the K04 commitment?

The hypothesis is conditional. MAIL-16 identifies attempt 3 as a button press that never returned an acknowledgement; the retained export does not establish that its payload is an authenticated printer output or that it is adjacent to ACK2 in one uninterrupted generator stream.

## Method

- Pin the retained spool, route, and acceptance files by SHA-256.
- Identify the selected attempt-2 ACK row by metadata only. Its payload is not parsed into the candidate path.
- Enumerate all (4! 	imes 2^4 = 384) permutations of the four 32-bit words and independent per-word endian choices for the later attempt-3 REQUESTED payload.
- For each view, apply the exact inverse of the lag-3 multiply-with-carry recurrence with multiplier (2{,}091{,}639). The recurrence gives a necessary carry bound; quotient/remainder inversion recovers the preceding four-word packet. A forward replay must reproduce the observed late packet.
- For each recovered 16-byte predecessor, apply the routed K04 mask and test the full K04 SHA-256 commitment. Candidate bytes and candidate hashes are never printed or written.

A deterministic synthetic positive control recovers a planted previous packet and passes the synthetic mask/commitment check.

## Result

| Check | Result |
|---|---:|
| Attempt-3 serializer views | 384 |
| Views satisfying Alea carry and inverse replay | 8 |
| Distinct preceding 16-byte packet candidates | 8 |
| K04 commitment hits | **0** |
| Synthetic reverse and commitment control | PASS |

## Interpretation and limits

This closes only the specific one-packet reverse-Alea hypothesis: treating the late REQUESTED3 payload as the immediately following four-word output block does not recover a commitment-matching K04 component. It does not establish that the printer used Alea/MWC3, that REQUESTED3 was emitted by the same producer, or that ACK2 and REQUESTED3 were adjacent in the original queue. The ACK2 payload remains unverified dispatch-log material; no historical media-integrity conclusion follows from this test.

Do not expand this into further seed, phase, serializer, or generator sweeps. A native PS-0417 queue/job image or an authenticated request/ACK binding is still required to establish the historical producer and adjacency.

No candidate, acceptance, routing, verifier, or source evidence was changed.
