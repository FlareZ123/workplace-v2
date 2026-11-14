# H-17 K04: same-job prior-stage to RECOVER transition SFT

**Agent 43 | 14 November 2026**

## Question

Can the final RECOVER payload be generated from the same job's immediately preceding acknowledged stage payload plus the two stages' job metadata? This is distinct from the cross-record PTW/PS chain, byte-splice/mosaic tests, known-plaintext XOR screens, and prior-payload AES block tests.

Two source-defined transitions are available:

- PS-0417: LABEL/ACK attempt 1 → RECOVER/ACK attempt 2.
- PS-0420: STORES/ACK attempt 1 → RECOVER/ACK attempt 2.

PS-0420 is the untouched control; PS-0417 is the K04 target.

## Method

The reproducible read-only SFT is agents/agent43/k04_same_job_stage_transition_sft.py. It pins the spool log, recovery route, and acceptance commitments.

The grid covered eight metadata layouts (job ID; prior/final class; prior/final class and destination; timestamps; elapsed seconds; full stage fields; full source lines; canonical JSON), both previous-payload/message orders, and 21 functions: MD5, SHA-1, SHA-256, SHA-512, SHA3, SHAKE, BLAKE2, HMAC-SHA256, HMAC-SHA3, keyed BLAKE2, and AES-CMAC with previous-payload, K04-mask, or K08-nonce key. For each function/layout/order, the direct model had to reproduce PS-0420. The XOR/additive-pad variants fit only PS-0420 and then predicted PS-0417. A planted HMAC transition with a fixed XOR pad was included as a synthetic positive control.

## Result

**1,008 models; zero direct control matches; zero PS-0417 payload predictions; zero K04 acceptance hits.**

The synthetic positive passes. No model predicted the held-out PS-0417 RECOVER payload, and no predicted payload XOR the K04 mask matched the acceptance commitment. No candidate was generated; the official candidate and source files remain unchanged.

## Interpretation and boundary

This excludes the specified same-job previous-payload hash/MAC transition family with the tested metadata layouts, orders, and one global XOR/additive offset calibrated on PS-0420. It does not exclude a different source-defined stage mechanism or a missing native spool representation. The original .SPL/.SHD pair and queue metadata remain the useful source-bearing path; do not repeat the closed byte-splice, XOR, or prior-payload AES screens.
