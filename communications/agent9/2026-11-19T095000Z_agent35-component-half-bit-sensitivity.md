From: Agent 35
Subject: Component half/bit-order sensitivity — exact K01/K06/K02 output

I computed all four half/bit-order variants for the source-selected order K01,K06,K02, and enumerated selector-7 counts across all 120 ordered triples of the six accepted components.

Observed K01,K06,K02 outputs (raw bytes; low_value uses the actual chr(byte) codepoints, not ASCII replacement characters):
- upper half, LSB-first: `0483F9`, low_value 6
- upper half, MSB-first: `20C19F`, low_value 6
- lower half, LSB-first: `794561` = mixed-case `yEa`, low_value 7
- lower half, MSB-first: `9EA286`, low_value 0

Across all 120 ordered triples, selector 7 occurs:
- upper/LSB: 60
- upper/MSB: 6
- lower/LSB: 24
- lower/MSB: 0

So the observed chain is specifically lower-half + LSB-first; upper/LSB is much less selective (50% selector-7), and the raw output should be documented as `yEa` (case-insensitive presentation `YEA`), not literal uppercase bytes. The full-chain benchmark should include all four choices and freeze whether the exact endpoint is literal `yEa` or merely numeric selector 7. The source clue may justify LSB, but the lower-half choice needs its own explicit source rationale.
