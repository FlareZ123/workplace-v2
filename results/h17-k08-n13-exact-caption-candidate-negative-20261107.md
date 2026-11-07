# K08 N13 exact Emily-caption candidate negative

**Date:** 2026-11-07  
**Source lead:** Agent 6 exact-candidate check communicated to Agent 43  
**Status:** exact wording rejected; no phrase variants tested.

## Candidate

The nearest complete N13 Emily caption for the late-watch/mugs/window context is:

> At the end of the night the mugs stood beside the window and somebody had remembered to leave the little lamp on.

Under the K08 normalization rule, the message is:

`at the end of the night the mugs stood beside the window and somebody had remembered to leave the little lamp on`

## Exact commitment test

- HMAC-SHA256 key: decoded K08 `desk_nonce` from `recovery-routing.json`.
- HMAC-SHA256 first 16 bytes: `26076C5426016BDB768A2B83E9F36857`.
- SHA-256 of those 16 bytes: `33e430295cb8ba51e8432fdab4a4da518c89ea8ee71dd2d3dc9fe09ee74f3d20`.
- The result does not match the K08 commitment.

## Interpretation

This rejects only this exact N13 caption wording. No alternative punctuation, capitalization, word order or phrase variants were tested. It does not establish that N13 is the source of Emily's final wording, and it does not exclude another caption, margin note or desk-note phrase. MAIL-14's original Emily desk notes and photo/galley captions remain the primary retrieval targets.

Agent 6 also reported a separate exact N12 workshop-card candidate negative; see `results/h17-k08-n12-workshop-card-candidate-20261107.md`. The N12 card remains a contextual/source-role control, not the keeper phrase.
