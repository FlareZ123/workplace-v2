# HST 128-row tail-bit carrier test (K04)

**Status:** negative, bounded exploratory test; not a source-authoritative derivation.

## Hypothesis

The eight-note ATEALBIT acrostic has an alternative BETA TAIL reading. One speculative interpretation is to take one tail/low bit from each HST row outside the K02 DIAG_WORD / GOOD / HOLD population. The HST export has 145 rows: 17 DIAG_WORD / GOOD / HOLD rows and 128 remaining rows (112 PV + 16 DIAG_WORD). That exact 128-row remainder can be packed into 16 bytes.

This is a weak cross-slot cue, not an authenticated rule. The telemetry readme explicitly classifies PV/engineering values as historian context rather than raw diagnostic words; K04's stated source is the ESC-N printer coupon.

## Frozen test

Source pins are embedded in hst_tailbit_carrier_sft.py. The script excludes all 17 DIAG_WORD / GOOD / HOLD rows, then tests three per-row tail-bit interpretations:

- PV decimal-thousandths LSB; DIAG_WORD numeric LSB
- PV binary64 representation LSB; DIAG_WORD numeric LSB
- PV binary32 representation LSB; DIAG_WORD numeric LSB

For each, it tests five deterministic row orders (retrieval, timestamp ascending/descending, sequence ascending, tag/sequence), forward/reverse row order, MSB/LSB bit packing, and raw/mask-XOR output. This is 120 complete 16-byte candidates. A synthetic 128-bit packing positive control passes.

## Result

- HST population: 145 rows
- Excluded K02 GOOD/HOLD diagnostic population: 17 rows
- Selected remainder: 128 rows = 112 PV + 16 DIAG_WORD
- Candidate checks: 120
- K04 SHA-256 hits: **0**
- Synthetic pack control: PASS

No candidate or official source file was changed. This closes only the specific one-tail-bit-per-row interpretation above; it does not prove that no other cross-slot encoding exists. Do not broaden into a generic bit-position/ordering grid without a new source-defined selector.
