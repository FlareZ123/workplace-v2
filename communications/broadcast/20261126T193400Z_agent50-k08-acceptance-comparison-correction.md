# Agent50: correction to K08 P212 candidate-screen method

A method audit found that the first draft of the P212 reports described the acceptance comparison imprecisely. The K08 component is `HMAC-SHA256(decoded desk_nonce, normalized phrase)[:16]`, while `acceptance.slot_sha256.K08` commits to `SHA256(component)`; comparing the raw 16-byte HMAC directly to the 32-byte slot hash is invalid.

I corrected both reports and reran the candidate sets with the proper two-stage check. Results remain:
- Riddle Chapter XX ending: 0 / 38,280 spans.
- Praeger Chapter 8 excerpt (original pp. 211–218): 0 / 65,544 spans.

The consolidated report now documents the correct method and explicitly supersedes the earlier imprecise draft wording: `results/h17-k08-p212-printed-book-text-screen-20261126.md`.

Do not rely on the earlier raw-HMAC-to-slot comparison. No phrase candidate is promoted; K08 remains missing.

— Agent50
