# K04 MT19937 low-bit randbelow(3) stage screen (2026-11-23)

## Question

Does the source-compatible K04 MT19937 chronology support a NumPy legacy RandomState-style `randint(0,3)` metadata sampler, using the low two tempered output bits with rejection of code 3, and a conditional route draw only for RECOVER rows?

This is distinct from the previously screened CPython `getrandbits(2)` top-bit sampler.

## Method

- Reused the existing conditional-route evaluator and all **170 source-compatible chronologies** across geometry families 950–955.
- Replaced only the metadata bit-plane interpretation with low-bit codes:
  `code = bit0 + 2*bit1`; code 3 is rejected.
- Screened the three call orders `class_route_dest`, `class_dest_route`, and `dest_class_route`.
- Screened current-row and next-row metadata binding, with the two existing leading-placement hypotheses.
- Retained the 95 training gaps and 32 held-out gaps.
- Added planted-positive controls for all three call orders using a seeded MT19937 stream with the low-bit mask/reject sampler. All three controls passed, so the evaluator can recover this model when it is present.
- The experiment did not load the selected ACK2 payload, K04 mask, or acceptance commitment.

Reproducible source and raw output:
- `agents/agent25/k04_numpy_lowbit_conditional_route_sampler_sft.py`
- `results/h17-k04-lowbit-metadata-screen-45093368403.txt`
- [GitHub Actions run 45093368403](https://github.com/FlareZ123/workplace-v2/actions/runs/45093368403)

## Result

**No low-bit conditional-route model survived.**

| Measure | Result |
|---|---:|
| Source-compatible chronologies | 170 |
| Geometry families | 950–955 |
| Training gaps | 95 |
| Held-out gaps | 32 |
| Best training mismatches | 24 |
| Zero-mismatch training models | 0 |
| Zero-mismatch held-out models | 0 |
| Surviving source route codebooks | 0 |
| Planted controls | 3/3 passed |

The model is rejected under the tested assumptions. In particular, changing from CPython-style top bits to NumPy-style low bits does not explain the source class/destination/route labels across the tested chronology family.

## Limits

This does not reject every possible NumPy API, metadata call schedule, or PRNG family. It rejects the specific two-`randbelow(3)` plus RECOVER-only conditional-route model, with the stated call orders, bindings, placements and source-compatible chronologies. It does not recover any K04 bits or establish a payload candidate.

## Next action

Do not repeat this same low-bit sampler family or the already-screened CPython top-bit variant. A materially different K04 attempt needs an event-stage rule tied to original job/attempt/copy semantics and must predict a complete held-out 16-byte packet before the acceptance commitment is consulted.
