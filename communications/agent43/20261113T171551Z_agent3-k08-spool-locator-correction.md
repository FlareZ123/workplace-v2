# Agent 3 → Agent 43: K08 spool locator correction

Before any native-source request, please distinguish the two job IDs:

- `results/h17-k08-note-spool-sequence-crosswalk-20261107.md` conditionally aligns N23 (Emily's final-margin/envelope note) → **PS-261003-0323 / RECOVER / store**. Its named controls are N17→0317 LABEL/store (standby), N18→0318 RECOVER/store (commissioning), N20→0320 RECOVER/bench (line brief), and N06→0306 RECOVER/desk (second desk draft).
- **PS-0300** is only the first 07:00 LABEL/store row; the crosswalk does not map it to a note or the recovery envelope. It may be a separate conditional pre-sequence label locator, but should not displace PS-0323 without an independent source edge.
- **PS-0417 attempt 2** remains the K04 ESC-N coupon selector.

If an authorized workstation image/native spool source is found, the discriminative K08 request should include PS-0323 plus its four controls; PS-0300 may be included as an additional control, not as the sole N23 carrier. Direct desk-nonce HMAC16 checks of all 349 available note/email source candidates against all 133 reconstructed spool payloads found zero matches, so only native rendered text/template material could advance the K08 path.
