# K08 component half/bit-order sensitivity

**Status:** reproducible source-selection sensitivity; not a full-chain null.

## Question

The existing downstream factorial reproducer fixes the lower half of each 16-byte accepted component and packs each byte's low bit LSB-first. This result enumerates the four obvious half/bit-order alternatives for the six accepted components and checks the exact source-selected order K01,K06,K02.

## Method

Reproducer: `agents/agent35/k08_component_half_bit_sensitivity.py`

Run:

```bash
python agents/agent35/k08_component_half_bit_sensitivity.py
```

The script reads the six accepted 16-byte values from the unchanged top-level `candidate.json`, enumerates all 120 ordered triples, and tests:
- upper vs lower 8-byte half;
- first extracted bit packed as LSB vs MSB;
- selector = `sum((ord(ch) & 1) << i)` over the exact `chr(byte)` output string.

No replacement-character ASCII decoding is used for non-ASCII bytes.

## Results

For the source-selected order K01,K06,K02:

| Half / bit order | Raw output | Text representation | Selector |
|---|---|---|---:|
| Upper / LSB | `0483F9` | non-text bytes | 6 |
| Upper / MSB | `20C19F` | non-text bytes | 6 |
| Lower / LSB | `794561` | `yEa` | 7 |
| Lower / MSB | `9EA286` | non-text bytes | 0 |

Across all 120 ordered triples, the number yielding numeric selector 7 is:

| Half / bit order | Selector-7 triples |
|---|---:|
| Upper / LSB | 60 |
| Upper / MSB | 6 |
| Lower / LSB | 24 |
| Lower / MSB | 0 |

Only the lower/LSB variant produces literal `YEA` under case-folding for any of the 120 triples (one occurrence, the observed K01,K06,K02 order). The raw bytes are `79 45 61`, so the exact rendered text is mixed-case `yEa`; `YEA` is a case-insensitive presentation, not the raw byte string.

## Interpretation and limits

The observed K01,K06,K02 → lower/LSB → `yEa` → selector 7 path is reproducible. However:
- the current 7,372,800-combination downstream null fixes lower/LSB and therefore does not cover these four half/bit-order alternatives;
- selector 7 is not unique across all component orders even under lower/LSB (24/120), and is much more common under upper/LSB (60/120);
- the source rationale for choosing the lower half must be stated separately from the rationale for extracting low bits;
- the full-chain benchmark must freeze whether the endpoint is literal `yEa` or merely numeric selector 7, and include all four half/bit-order choices.

This result does not recover K08 and does not alter any accepted component.
