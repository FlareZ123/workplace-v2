# Shared-phrase K04/K08 HMAC probe

**Date:** 2026-11-25  
**Agent:** Agent 2  
**Status:** bounded negative result; no component recovered

## Hypothesis

A single normalized keeper phrase might feed both missing slots:

- K08: `HMAC-SHA256(desk_nonce, phrase)[:16]`.
- K04: the PS-0417 attempt-2 RECOVER ACK payload might be `HMAC-SHA256(K04_mask, phrase)[:16]`, with the published K04 reduction still applied afterward: `component = ACK_payload XOR K04_mask`.

This challenges the assumption that K04's printer payload and K08's keeper phrase are independent source objects. It is an exploratory model, not an accepted source rule.

## Test

The reproducible probe at [`work/h17_k04_k08_shared_phrase_hmac_probe.py`](../work/h17_k04_k08_shared_phrase_hmac_probe.py):

1. Reads the supplied archive ZIP, the route constants, and the acceptance commitments.
2. Selects the PS-0417 attempt-2 RECOVER ACK payload.
3. Extracts every contiguous normalized span of 1–24 words from the 24 desk/noticeboard notes, all 20 plain-text email bodies, and the galley/stores log.
4. Tests the exact K08 HMAC commitment, the K04 payload-as-HMAC construction, the resulting masked K04 component, and reverse-key-order controls.

The scan produced **17,480 unique normalized spans** from **22 text sources**. A separate direct implementation produced the same count and zero hits.

## Result

No candidate matched either acceptance commitment. In particular:

- no retained-export phrase produced the K08 component;
- no retained-export phrase produced the PS-0417 ACK payload under the K04 mask;
- no resulting K04 component matched the K04 commitment;
- reversing HMAC key/message order did not produce a match.

## Interpretation

This closes the specific *shared normalized phrase → two keyed outputs* construction over the retained text. It does **not** rule out a phrase present only in the missing original envelope face, Emily's margin/version history, or photograph captions. Nor does it establish that the dispatch ACK is the physical coupon.

The current evidence boundary remains unchanged: K04 still needs the native PS-0417 queue/job or physical coupon record; K08 still needs the final envelope wording or its authoring source. Do not rerun this same text-span/HMAC family against the same export.
