# K08 literal HMAC16-to-printer-label carrier join

**Agent 44, 7 November 2026. Result: no exact source-to-object match.**

## Question

Could a literal phrase preserved in one of the 24 crew-board/photo/desk-note entries have been normalized under the K08 rule, HMAC-SHA256 keyed by the original desk nonce, truncated to 16 bytes, and retained verbatim as a 16-byte printer payload? This would be a direct text-to-object bridge, potentially identifying a known caption's HMAC component in a retained LABEL packet.

This test is deliberately narrower than general label transport: it asks for exact equality of one source phrase's HMAC16 output to one original spool payload. It does not assume a shared mask, permutation, additive offset, or other transformation.

## Frozen method

1. Pin the original notes, spool and route-file SHA256 values:
   - notes: `13f2318c...c05858e8b8983c5cb`
   - spool: `7d71d8be...3841b6083`
   - routing: `f8fcbca7...a4764d8a5`
2. Parse all 24 `N01..N24` note entries. Remove only the leading caption/role label through its first colon, where present.
3. Apply the exact K08 normalization: lowercase, replace non-`[a-z0-9 whitespace]` characters with spaces, collapse whitespace.
4. Enumerate every contiguous 1–40-word span from each note. This yields **2,919 source-span occurrences** and **2,751 unique normalized spans**.
5. Compute exactly `HMAC-SHA256(desk_nonce, normalized_utf8)[:16]`.
6. Compare each 16-byte result against all **52 intact CLASS=LABEL packets**, then against the **132 intact packets across all classes**.
7. Select the disputed K04 ACK2 from header fields only and exclude it before parsing any payload. The selected row is zero-based record index **129**. No K04 target bytes are used.
8. Verify the scanner with a synthetic planted exact HMAC16 label.

## Result

| Measure | Result |
|---|---:|
| Note entries | 24 |
| Unique normalized spans | 2,751 |
| Total span occurrences | 2,919 |
| Intact LABEL payloads | 52 |
| Intact all-class payloads | 132 |
| Exact HMAC16-to-LABEL matches | **0** |
| Exact HMAC16-to-any-intact-payload matches | **0** |
| Synthetic planted positive | PASS |

The N02 known HMAC16 control reproduces `BF889359B0303F2B2B2FD96AE841210B`. The selected K04 payload is never parsed. The K08 acceptance commitment is not consulted because no source-to-payload hit was found.

Reproducer: [`agents/agent44/k08_hmac_label_carrier_sft.py`](../agents/agent44/k08_hmac_label_carrier_sft.py).

## Relation to prior work

This is distinct from:

- Agent 5's [known-label transport calibration](h17-k08-printer-label-known-plaintext-transport-20261105.md), which tests pairwise differences under shared XOR/additive masks and arbitrary common byte permutations. It does not test a single known HMAC16 value appearing verbatim as a packet.
- Agent 47's [binary component source-pair test](../agents/agent47/k08_binary_component_source_pair_sft.py), which includes known-note HMAC16 values among its source fields but constructs pairwise component candidates.
- Earlier literal phrase-span searches against the K08 acceptance commitment. Here the tested relation is the intermediate HMAC16 value to an original printer payload, not the final SHA256 commitment.

## Interpretation and limits

The frozen direct-equality mechanism is excluded for all contiguous 1–40-word spans in the 24 preserved notes and all intact supplied spool packets. The test does **not** exclude:

- an edited or combined phrase that is not a contiguous note span;
- the missing original keeper-envelope/margin text;
- an output transformed by a job-specific or nonlinear printer/capture mechanism;
- a physical label or print record absent from the supplied export;
- an unrelated spool payload that is not a K08 object.

No final K08 wording, K08 component, or K04 byte was recovered. Six original slots remain PASS; K04 and K08 remain MISSING; the combined recovery remains INCOMPLETE. Further label-transform variants should require a new source-defined transport rule or an independent original label witness.
