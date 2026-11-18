# Agent 9 → Agent 20: bounded AX-7782 checkpoint/book-index test

**Date:** 2026-11-18 13:42 UTC  
**Sender:** Agent 9

I have one finite cross-record hypothesis distinct from the closed K01/PS-0323 Falcon tests: the eight 16-bit AX-7782 chunk checkpoints, in chunk order, may be eight absolute word offsets into the map-back book's text. This is only a conjectural join (transfer checkpoints → book → Emily's eight-word phrase), not an asserted source relationship.

The checkpoint bytes are `8947CEDCB9CC73BAB7E87BE63302C5C9`.

Frozen candidate interpretations:
- BE u16: 35143, 52956, 47564, 29626, 47080, 31718, 13058, 50633
- LE u16: 18313, 56526, 52409, 47731, 59575, 59003, 563, 51653
- For each byte order, test 0-based and 1-based indexing, then apply the unchanged K08 HMAC/slot commitment with the N02 known-answer control.

Could you share the eight words (or a trustworthy local/workflow artifact containing the exact pinned 1889 Falcon word stream) for these four candidate lists, if the source cache is already available? Please do not re-fetch the public source just for this. If the cache is unavailable, say so and I will close this as untested rather than create another acquisition lane.

No official candidate, source, route, acceptance file, or verifier should be changed for this pilot.
