# PS-0417 retry-to-K08 note-graph screen

**Agent:** 50  
**Date:** 2026-11-25  
**Scope:** One bounded, source-derived cross-slot experiment. This is not a recovered K04 or K08 component.

## Question

Does the same-job retry history for the K04 printer job provide an independent bridge into the K08 keeper-note corpus, and can that bridge produce a complete phrase candidate that satisfies the K08 commitment?

## Construction

The K04 source is `resources/evidence/print/spool-reconstruction.log`; the K08 source is `resources/evidence/crew/noticeboard-and-desk-notes.txt`, with the nonce and normalization rule in `resources/evidence/recovery-routing.json`.

1. Keep the PS-0417 rows distinct by class and attempt. The earlier LABEL acknowledgement is not a RECOVER payload. The selected RECOVER input remains attempt 2 ACK; attempt 3 REQUESTED is used only as a control and is not promoted to an acknowledged payload.
2. Apply the already-used LOW-BIT note-selector operation to the attempt payloads and to the attempt-2 payload after the prescribed K04 XOR mask.
3. Follow the resulting note selectors through the existing K08 HMAC-derived note-selector graph.
4. As a complete-output test, form a deliberately narrow collage hypothesis from four source-anchor notes: N01 and N05 are the raw/masked attempt selectors, while N09 and N13 lie on the two downstream HMAC-selector routes. Test exact contiguous-word spans in the candidate order N01, N05, N09, N13. Require each span to retain its source anchor: N01 contains “sea”; N05 contains “boat”, “crossing”, or “biscuits”; N09 contains either “cup” and “alone” or “bad” and “night”; N13 contains “night” and either “mugs” or “window”. Join the four spans with spaces, apply the exact K08 normalization, compute HMAC-SHA256 with the desk nonce, truncate to 16 bytes, and compare SHA-256 with the K08 commitment.

## Result

- The masked attempt-2 selector agrees with the LOW-BIT selector of the subsequent attempt-3 REQUESTED row. This is a same-job control relation, not evidence that attempt 3 was acknowledged or should replace attempt 2.
- The selector-derived note graph has two routes into the Emily-authored N13 node: one route begins at N01 and passes through N06/N10; the other begins at N05 and passes through N09/N12/N11. This is a plausible cross-slot locator for the authoring cluster, not a phrase reconstruction.
- The note selector is not unique across the spool population. In particular, the selected RECOVER ACK is not uniquely identified by this selector alone.
- The prescribed K04 XOR candidate still does **not** satisfy the K04 acceptance commitment.
- The exact-span construction evaluated **6,336,000** complete normalized phrase candidates and produced **zero** K08 commitment hits.

## Interpretation

This is a new, bounded retry-to-note-graph relation, but it does not recover either missing component. It falsifies this specific space-joined exact-span collage hypothesis over N01/N05/N09/N13. It does not test arbitrary edits or establish that the HMAC-selector paths are phrase-authoring instructions. The note graph remains a locator hypothesis only; the low-bit selector is not a source-authenticated phrase-authoring rule.

Do not use the unacknowledged attempt-3 payload as the K04 coupon, do not claim the K04 XOR candidate is accepted, and do not expand this into unconstrained paraphrase generation. The next high-value evidence is the native PS-0417 coupon/spool object or the original desk/envelope/photo carrier, not another selector permutation.

## Reproduction outline

Use the exact spool rows and note bodies above. For each joined candidate phrase `p`, compute:

```python
normalized = " ".join(re.sub(r"[^a-z0-9\s]", " ", p.lower()).split())
candidate = hmac.new(desk_nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
hit = hashlib.sha256(candidate).hexdigest() == acceptance["slot_sha256"]["K08"]
```

The run reports only aggregate counts and commitment-hit status; it does not emit candidate bytes, the K04 mask, the desk nonce, or HMAC values.
