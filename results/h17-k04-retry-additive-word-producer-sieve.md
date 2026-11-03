# K04: same-job 32-bit additive retry producer, exact complete-candidate falsifier

**Agent 2, 3 November 2026. Original complete K04 matches: 0.** The six previously recovered components remain PASS; K04 and K08 are missing and combined acceptance is INCOMPLETE.

## Proposed mechanism and novelty

The original source contains four distinct records for printer job `PS-261003-0417`: a 16:45 LABEL ACK, an 18:01 RECOVER requested attempt 1, an 18:02 RECOVER ACK attempt 2, and an 18:03 RECOVER requested attempt 3. The selected physical ACK proves dispatch, but the retained reconstructed payload lacks independent integrity authentication. A possible upstream retry-accumulator could produce a coupon by **adding source 32-bit words with carry modulo 2^32**, instead of the XOR subset already excluded by [Agent 5's retry-word experiment](h17-k04-retry-xor-word-producer-sieve.md). The source does **not** attest this additive producer, so this is a conditional, direct complete-candidate test.

For each of four corresponding little-endian 32-bit word lanes, choose **one of 15 nonempty subsets** of the four source buffers. Add those source words modulo 2^32; optionally reverse the resulting four bytes independently for each lane; finally permute the four lanes into any of 24 orders. XOR the constructed 16-byte coupon with the original unmodified route mask, SHA-256 the 16-byte K04 component, and compare to the original unmodified slot commitment.

Exactly `15^4 × 2^4 × 4! = 19,440,000` complete component assignments were enumerated. The exhaustive test is separate from per-word XOR subset/reorder (same candidate count, different arithmetic) and byte-select mosaics (which cannot generate carry bytes).

## Original-source result and controls

- Original spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The program refuses a different source and checks all four specific job records before enumeration.
- Original 16-byte mask: `8556C8CB6140A7F9A5123AC7571BEE1C`.
- Original K04 SHA256 commitment: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.
- **Observed:** 19,440,000 candidate checks, **zero** original matches; synthetic planted positive candidate recovered **exactly once**.
- Two independent implementations produced the same result against the unchanged locally supplied ZIP: compiled C++/OpenSSL, 6.423 seconds, and the portable standard-library Python SFT, 8.517 seconds. Execution durations are environment-specific and do not establish historical fitness.

The canonical [reproducible single-file test](../agents/agent2/k04_retry_additive_sft.py) uses Python standard library. Pass it a path to the original `evidence/print/spool-reconstruction.log`; it does not write source files, alter original checker/commitments, or require Work mode.

## Interpretation

This excludes a complete, specified **word-wise additive retry-accumulator** family using any subset of the four surviving same-job buffers and independent word endian/permutation operations. It does not exclude a different producer, a mixed XOR/add operation, cross-offset byte/word sourcing, unknown operands, a different mask, or a historical physical coupon absent from the reconstructed spool. In particular, no original selected K04 bits are authenticated by this negative. K08 exact final author wording is not implicated.

Subsequent experiments should prioritize a causal reason to expect a specific upstream accumulator or output-index rule, rather than enumerating ever-larger unconstrained donor arithmetic.
