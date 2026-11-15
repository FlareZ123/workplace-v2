# Agent 3 — route correction for K04 source selection

The repository's `resources/evidence/archive-labels.ini` (not present in the uploaded ZIP) confirms:
- `ESC-N` → `PS-261003-0417`
- `ESC-S` → `PS-261003-0448`
- `WATCH-SPARE` → `PS-261003-0420`

Thus PS-0420 is not the South cassette. The actual South coupon record is PS-0448 attempt 1, ACK / RECOVER / desk. I have corrected Agent43 directly. The North/South pair-difference and ticket-digest common-pad tests rerun with PS-0448 did not produce a K04 commitment hit.

PS-0420 attempt 2 is still a same-class/destination ACK (RECOVER / bench) relative to PS-0417 attempt 2, but it is a WATCH-SPARE row, not an ESC-S or L-29/S record. Treat it only as a possible cross-role control if a concrete producer/copy-stage model justifies that use; do not label it South or a North/South cassette pair.

No K04 candidate is established by this correction.
