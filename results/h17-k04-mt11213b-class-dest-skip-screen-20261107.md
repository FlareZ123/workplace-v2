# H-17 K04: MT11213b metadata-driven skip screen

**Date:** 2026-11-07  
**Agent:** 44  
**Disposition:** bounded negative result; no K04 candidate recovered

## Question

Could the printer payloads be outputs from one MT11213b stream where each packet consumes four 32-bit output words plus a deterministic number of hidden words selected by the observed `CLASS` and/or `DEST` fields?

This is a new conditional variant of the fixed-gap MT11213b screen in `agents/agent7/k04_mt11213b_351phase_variable_gap_sft.py`. It uses the spool's actual metadata as the gap selector. It does not fit arbitrary per-record gaps.

## Pinned inputs

All hashes are SHA-256.

| Input | SHA-256 |
|---|---|
| Supplied archive ZIP | `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7` |
| `evidence/print/spool-reconstruction.log` | `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` |
| `evidence/recovery-routing.json` | `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5` |
| `acceptance.json` | `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f` |

The first 128 ACK events are the ordinary jobs PS-261003-0300 through PS-261003-0427. The selected PS-261003-0417 RECOVER ACK2 is excluded from fitting and holdout. The first 120 ordinary packets form the training set; jobs 0420-0427 are eight whole-packet holdouts.

## Model and test

The MT11213b engine uses the 351-word state and recurrence already implemented in Agent 7's SFT. Each 16-byte packet is decoded as four 32-bit outputs. Four serializers were tested: little- and big-endian words, each with forward and reversed word order.

For a packet at index r, its stream start is:

`start[r] = phase + sum(4 + gap[q], q < r)`

The bounded gap families were:

1. One fixed extra-word cost per CLASS (LABEL, STORES, RECOVER), each cost 0-4, at phase 0.
2. One fixed extra-word cost per DEST (bench, desk, store), each cost 0-4, at phase 0.
3. Additive CLASS and DEST costs, each 0-2, at phase 0.
4. One binary extra-word cost per observed CLASS/DEST pair, at phase 0.
5. A phase screen at 0, 175, and 350 for CLASS-only and DEST-only costs 0-2, and additive CLASS/DEST costs 0-1.

Each candidate had to yield a unique state from the first 120 packets and reproduce every whole-packet holdout exactly. The screen also tested a request-inclusive variant: the first PS-261003-0417 REQUESTED row was appended after the 128 ACK packets as a ninth holdout. The selected ACK2 remained excluded and was the next predicted packet after that request row.

The completed grids comprised 8,796 solver attempts across the four serializers. The broader all-351-phase search for the variable-gap families was not run.

## Result

**No candidate survived.** None of the completed gap/phase/serialization combinations produced a unique state that exactly reproduced all eight ordinary holdouts. The request-inclusive variant also produced no model that reproduced all nine holdouts.

No model prediction for the selected ACK2 was therefore accepted or tested as a K04 candidate. No source bytes were changed.

## Interpretation and limits

This rejects only the bounded metadata-driven MT11213b families listed above. It does not reject every variable-gap MT model, other generator families, or a different source-to-coupon relationship. In particular, the phase search for variable gaps was sampled at three phases rather than exhaustively searched.

Do not expand this into unconstrained per-record gap fitting. That would introduce enough free choices to overfit the training packets and would not establish a source mechanism. A future model should specify its gap rule from independent printer/driver evidence and preserve a predeclared intact whole-packet holdout.

The practical next step remains acquisition of an authenticated physical North L-29/N coupon/copy witness or a provenance-linked original printer capture record. The spool ACK establishes receipt; it does not independently authenticate the media payload.
