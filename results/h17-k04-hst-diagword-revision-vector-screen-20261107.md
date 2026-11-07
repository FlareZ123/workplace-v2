# HST-4 DIAG_WORD revision vectors as K04 candidates

**Owner:** Agent 34  
**Date:** 2026-11-07  
**Status:** bounded cross-source candidate family rejected; no K04 bytes recovered  
**Reproduction:** `python agents/agent34/k04_hst_diagword_revision_vector_sft.py`

## Question

Could a complete eight-word HST-4 `LT-204 / DIAG_WORD` revision block be the 16-byte K04 component or the opaque 16-byte K04 payload? This is a narrowly source-defined cross-slot hypothesis: the telemetry export contains four complete, revision-scoped eight-sample blocks, each of which naturally serializes to 16 bytes.

## Source semantics and positive control

The original `export-readme.txt` identifies `DIAG_WORD` as an unsigned raw 16-bit recorder field. It states that revision is scoped to `(tag, field, seq)`, that newer SUSPECT or RUN samples do not supersede GOOD/HOLD diagnostic samples, and that the acquisition interval's end is exclusive.

The export contains four complete `LT-204 / DIAG_WORD` blocks, each with seq 0–7:

| Revision | Quality | State | Interpretation |
|---:|---|---|---|
| 1 | GOOD | HOLD | Earlier eligible snapshot |
| 2 | GOOD | HOLD | Selected by the K02 reducer |
| 3 | SUSPECT | HOLD | Excluded by quality |
| 4 | GOOD | RUN | Excluded by state |

A separate revision-99 seq-7 value is timestamped exactly at the exclusive end and belongs to the next freeze; it is not part of any eight-word candidate block.

The SFT independently reproduces the original K02 reducer, including UTC offset handling and greatest-revision selection. It selects revision 2 for all eight sequence values. The big-endian raw vector is `E1A5E474BAD7E853A2E8C71D3317D507`; hashing it and retaining the first 16 digest bytes yields component `0D7E3AB56FB75DA3EB0E2E06786D239E`, whose SHA-256 matches the original K02 commitment. This is the positive control for the field grouping and serialization.

## K04 candidate screen

For each complete revision block (1–4), the SFT tests both 16-bit byte orders, preserving seq order 0–7. Each 16-byte vector is tested in two source interpretations:

1. The vector itself is the K04 component.
2. The vector is the opaque K04 payload, so the original `masked_component` is XORed before checking the component commitment.

That is 4 revisions × 2 byte orders × 2 interpretations = **16 complete-block candidates**. As a second, source-bounded delta family, the two complete GOOD/HOLD revisions (1 and 2) are also XORed per seq in both byte orders, each tested directly and after the K04 mask: **4 additional candidates**. The original K04 SHA-256 commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

**Result: zero of 20 candidates match.** The SFT does not read the disputed PS-0417 ACK2 payload and does not modify the candidate, acceptance file, routing rules or verifier.

## Interpretation and limits

This excludes exact reuse of one complete HST-4 revision block as K04, under the two 16-bit serializations tested and with or without the official K04 mask, including the per-seq XOR delta between the two eligible GOOD/HOLD revisions. It does not establish that HST-4 and the printer share a producer, and it does not exclude arbitrary transformations or a different source object. No K04 bits are authenticated by this result.

The result is useful mainly as a stop condition: do not keep treating the four complete `DIAG_WORD` revision blocks as direct K04 coupon/payload candidates. The next valuable K04 evidence remains an independently retained original coupon, native PS-0417 job object, or a source-authenticated copy-stage/integrity record. K08 is unaffected.

**Confidence:** high in the 16-candidate exclusion and K02 positive control; low in the historical relevance of the cross-slot hypothesis.
