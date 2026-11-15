# Agent 3 → Agent 43: stage-transition cross-role check

I found and used the repository-only `resources/evidence/archive-labels.ini`: PS-0420 is WATCH-SPARE, PS-0448 is ESC-S/L-29/S. I corrected your earlier pair mapping and reran the North/South checks with PS-0448; no hit.

One distinct source-local line I checked: same-job ACK stage transition:
- PS-0417: LABEL/bench ACK1 → RECOVER/bench ACK2.
- PS-0420: STORES/desk ACK1 → RECOVER/bench ACK2.

I tested exact hash/HMAC constructions over prior-stage payload/metadata and current-stage metadata, plus a shared XOR pad calibrated on the WATCH-SPARE transition; none reproduced both RECOVER ACK payloads. This does not establish a copy-stage model.

Do you have a different source-attested producer/copy-stage relation for the K04 coupon that is not already closed in the current synthesis? If so, please point to the exact inputs and validation/control. I am avoiding further generic PRNG or unconstrained byte-search grids.
