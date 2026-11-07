# AX checkpoint retry-delta vectors as K04 candidates

**Owner:** Agent 34  
**Date:** 2026-11-07  
**Status:** bounded source-derived candidate family rejected; no K04 bytes recovered  
**Reproduction:** `python agents/agent34/k04_ax_retry_delta_sft.py`

## Question

The transfer audit preserves two 2-byte checkpoint attempts for each of eight chunk sequence numbers, for each of four AX transfers. Could the per-chunk retry difference, concatenated in sequence order, be the 16-byte K04 component or opaque K04 payload?

This is distinct from treating one attempt's eight checkpoints as a 16-byte vector. It is also distinct from per-word old/new retry-operator tests: here the complete 16-byte XOR-delta vector is the candidate object.

## Source handling and positive control

The SFT pins the original transfer audit, recovery-routing file and acceptance file. It requires exactly one attempt 1 and attempt 2 for every seq 0–7 in all four transfer IDs. The transfer queue note identifies AX-7778 as a pre-incident drill, AX-7781 as a dry run, and AX-7783 as stopped before handoff. The original K07 rule selects AX-7782, greatest attempt per seq, and requires a non-dry-run COMMIT.

As a positive control, the SFT rebuilds the AX-7782 attempt-2 vector in seq order:
`8947CEDCB9CC73BAB7E87BE63302C5C9`.

Applying the official K07 reducer (SHA-256, first 16 digest bytes) yields:
`93495F5E425AB8E592123DABAEB68545`,
whose SHA-256 matches the original K07 acceptance commitment. This validates the transfer parsing, sequence order and selected-attempt control.

## Candidate construction

For each transfer and each seq, compute the two-byte value:

`delta[seq] = checkpoint(seq, attempt=1) XOR checkpoint(seq, attempt=2)`.

Concatenate the eight two-byte deltas in seq order to obtain a 16-byte vector. Test two interpretations:

1. The retry-delta vector is already the K04 component.
2. The retry-delta vector is the opaque K04 payload, so XOR it with the original K04 mask before checking the component commitment.

Four transfers × two interpretations produce **8 complete candidates**. The selected AX-7782 delta vector is `EB6383274A74B987AF6089CC0EB242A0`; after the official K04 mask it becomes `6E354BEC2B341E7E0A72B30B59ACBC`.

**Result: zero of eight candidates match** the unchanged K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The disputed PS-0417 ACK2 payload is never read. The candidate, acceptance, routing rules and verifier are unchanged.

## Interpretation and limits

This excludes exact reuse of the per-seq attempt1/attempt2 XOR-delta vector from any of the four preserved AX transfers, either directly or as the payload before the official K04 mask. It does not establish a historical link between transfer retries and the printer coupon, and it does not exclude other retry-derived transforms or an independently retained native coupon.

The result is a small, source-grounded stop condition. Do not expand it into arbitrary checkpoint permutations or wider XOR mosaics without a separate source rule. The highest-value K04 evidence remains an independently retained original ESC-N coupon/native spool object or a source-authenticated copy-stage integrity record. K08 is unaffected.

**Confidence:** high in the exact source parsing, K07 positive control and eight-candidate exclusion; low in the historical relevance of the retry-delta hypothesis.
