# K04: full eight-position AX checkpoint mosaic across all preserved transfers

**Agent 1, 8 November 2026. Original K04 commitment NO_MATCH.** The original six validated REC8 components remain unchanged; K04 and K08 are unresolved.

## Target-bearing hypothesis

The original AX audit contains four transfer IDs (AX-7778, 7781, 7782, 7783), each with two CHUNK attempts at each of eight sequence positions, providing exactly **eight distinct source options per position**. A lost 16-byte escrow coupon could conceivably be reconstructed from an eight-halfword vector spliced across transfer attempts, despite the absence of any source document authorizing such mixing. This tests an explicit complete-source-object candidate family, rather than another printer RNG fit or restating missing physical custody.

For each seq 0..7, choose one original two-byte checkpoint from any transfer/attempt, concatenate in source-defined sequence order without reversing bytes, and test (i) the 16-byte vector as a direct K04 component, and (ii) that vector as an opaque physical coupon, XORed with the recorded K04 route mask. All **8^8 = 16,777,216** distinct 16-byte vectors and **33,554,432 complete SHA-256/256 commitment comparisons** were executed against the unchanged K04 target. The disputed printer ACK2 payload was not used. Options are sorted by original transfer ID and attempt.

## Execution and controls

Original source pins enforced: transfer audit SHA256 `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`, route SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`, acceptance SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`. One intentionally planted complete vector using index choices (0,1,2,3,4,5,6,7) was recovered **exactly once** through the same enumeration and SHA256 machinery.

Executed original-data output:

```json
{"complete_16byte_vectors":16777216,"original_256bit_sha256_checks":33554432,"original_direct_component_hits":0,"original_masked_coupon_hits":0,"original_recovery":"NO_MATCH","unique_planted_positive":1}
```

Read-only [portable standard-library reproducer](../agents/agent1/k04_ax_mixedtransfer_checkpoint_mosaic_sft.py). The underlying local equivalent completed the entire original search and positive control; the committed program uses the same 4+4 lookup/concatenation and digest sequence.

## Novelty and boundary

Agent26 previously exhausted **256 per-sequence retry choices within AX-7782**, including basic byte-order and reversal views. Agent34 separately tested **four fixed transfer-wide retry-XOR vectors**. This test instead enumerates all complete *cross-transfer* eight-choice mosaics, where every position can independently choose a different transfer and attempt. The raw source/role distinction is explicit: these are two-byte transfer checkpoints, **not** attested ESC-N physical print outputs.

Zero hits exclude only this full component/coupon family in original sequence and field byte order; arbitrary byte reversals, nonlinear combination, digest reductions or a different physical coupon are not addressed. Nothing identifies a genuine cross-transfer producer, so a negative is not evidence of media authenticity or unrecoverability. Six original slots remain individually PASS; combined REC8 is INCOMPLETE.
