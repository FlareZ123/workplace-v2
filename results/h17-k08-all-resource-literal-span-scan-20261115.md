# K08 exact literal spans across all textual evidence sources

**Agent 6 · 15 November 2026 · original K08 commitment: no match.**

## Question

Does the exact normalized keeper phrase already occur as a contiguous span in any textual source file in the supplied evidence export?

## Frozen source and method

The scan covers all **40 textual files** under `resources/evidence/`: crew and galley notes, all 20 EMLs and their index, maintenance records, printer reconstruction, telemetry, transfer audit, procedure scans, supplemental office material, and the routing file. The binary recorder dump and PDF are outside this text-only test.

The ordered path-and-byte manifest SHA-256 is `908762b3ab5228d1034b850613c10daa58ba68d13a0e446a97dc5a0be35d0457`. The supplied ZIP SHA-256 is `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`.

For each file independently, apply the official K08 normalization (lowercase; replace non-ASCII-alphanumeric, non-whitespace characters with spaces; collapse whitespace), then enumerate every contiguous span of 1–64 words. For each unique normalized phrase, compute HMAC-SHA256 with the route's decoded 16-byte desk nonce, retain the first 16 bytes, and compare SHA-256 of those 16 bytes against the unchanged K08 commitment.

## Executed result

```text
text_evidence_files                 40
normalized_words                16,355
span_occurrences               966,116
unique_normalized_phrases      900,769
word_lengths                     1..64
original_K08_commitment_hits         0
N02_HMAC16_control                PASS
synthetic_complete_reducer_control PASS
```

The known Emily N02 phrase reproduces HMAC16 `BF889359B0303F2B2B2FD96AE841210B`. The independent planted positive also passes the complete HMAC16-to-SHA256 reducer.

## Interpretation and boundary

No literal contiguous 1–64-word span in the 40 textual evidence files produces the original K08 commitment. This is a source-bounded negative only: it does not exclude paraphrase, noncontiguous assembly, a phrase longer than 64 words, a hidden phrase in the PDF or binary recorder, omitted native mail, or the missing envelope/photo-caption/profile sources. It recovers no K08 word and does not change the acceptance state.

Reproducer: `agents/agent6/k08_all_resource_literal_span_sft.py`. The script verifies the full text-source manifest, routing and acceptance hashes, the N02 known-phrase control, the synthetic reducer control, and the exact candidate counts before reporting.

No candidate, acceptance commitment, route, source resource, or official verifier was modified.
