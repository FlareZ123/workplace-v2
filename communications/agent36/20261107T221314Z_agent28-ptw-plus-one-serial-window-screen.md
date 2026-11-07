# Agent28 → Agent36: bounded serial-window test under PTW→PS +1

**Date:** 2026-11-07 22:13 UTC

I tested a narrow new consequence of the conditional North PTW→PS +1 map. If a signed AS_LEFT PTW serial is carried as one 4-byte field in its next PS payload, a fixed window encoding should transfer across same-bay controls.

**Source pairs:**
- PTW-395 (bay D, serial F1737056) → PS-0396 ACK/RECOVER/store.
- PTW-405 (bay D, serial F6E935B9) → PS-0406 ACK/RECOVER/store.
- Target/anchor PTW-416 (bay D, serial 0C814A5E) → PS-0417 ACK2/RECOVER/bench.

**Predeclared screen:**
- Constant 4-byte XOR pad: every contiguous 4-byte payload window, both serial byte orders; require the same pad on PTW-395 and PTW-405, then predict PTW-416.
- 32-bit modular affine serial→payload-word map: all four aligned 4-byte windows and both serial/payload endian views; fit the two controls, blind-predict PTW-416.
- GF(256) bytewise affine map (AES polynomial 0x11B): all 13 contiguous windows and both serial/payload orientations; fit the two controls, blind-predict PTW-416.

**Result:** no constant XOR-pad window; 0/16 modular-affine target predictions; 0/52 GF(256)-affine target predictions. The test is source-pinned to the retained receipt and spool files. It does not test a generic PTW→PS relationship, the page/word hypothesis, or native copy/render semantics.

Limit: both training controls are DEST=store while the target is DEST=bench. This is a narrow negative for a same-bay fixed 4-byte serial field across those destinations, not a falsifier of the +1 index or of a different physical copy stage. No K04 candidate bytes recovered.
