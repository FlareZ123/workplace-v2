# H-17 K04: stateful PTW/PS record-ID reducer SFT

**Agent 43 | 14 November 2026**

## Question

Could the 27 same-number PTW-390..416 / PS-390..416 historical pairs be outputs of a stateful archive reducer? If so, the prior ACK payload would be the state, the current permit serial and public job metadata would be the next input, and the same rule could predict the held-out PS-0417 RECOVER payload from PS-0416 plus the PTW-417 signed serial block.

This is a source-defined cross-record hypothesis, not an assertion that numeric ID equality proves a common writer.

## Method

The reproducible read-only SFT is [`agents/agent43/k04_stateful_recordid_chain_sft.py`](../agents/agent43/k04_stateful_recordid_chain_sft.py). It pins the spool log, seal receipts, MAIL-04 closeout order, recovery-routing parameters, and acceptance commitments.

- Controls: one ACK packet for each matched PTW/PS ID 390..416 (27 pairs, 26 state transitions).
- Source serial representations: raw bytes, reversed raw bytes, uppercase hex ASCII, and full SG serial text.
- Eight message contexts: serial only; job ID; permit ID; job/class/destination; permit/bay; timestamp/job/class/destination; full job/attempt/state/class/destination/timestamp; and canonical JSON.
- Two state/message concatenation orders.
- Eighteen 128-bit output functions: MD5, SHA-1, SHA-256 first/last halves, SHA-512 first/last halves, SHA3-256 first/last halves, BLAKE2s/BLAKE2b-128, SHAKE128/SHAKE256-128, HMAC-SHA256 with prior-state or message key, HMAC-SHA3-256 with prior-state or message key, and keyed BLAKE2s/BLAKE2b with prior-state key.
- Three output rules: direct; one global XOR pad fitted on transition 390→391; or one global additive pad modulo 2^128 fitted on that transition.

The direct models must predict all 26 transitions. Padded models are calibrated on the first transition and must predict the remaining 25. A planted HMAC-SHA256 previous-state chain with a fixed XOR pad is included as a synthetic positive control.

## Result

**Reproducible SFT:** 3,456 models; zero exact historical holdouts.

| Measure | Result |
|---|---:|
| Direct models | 1,152; all scored 0/26 |
| Padded models | 2,304; all scored 0/25 |
| Maximum exact holdouts | 0 |
| Models with any exact holdout | 0 |
| Synthetic planted holdouts | 25/25 |

The synthetic positive passes, so the pad-fit and holdout path is exercised. The target source block was independently selected from the highest signed CLOSED AS_LEFT PTW-417 revision per bay, in MAIL-04 order B,D,A,C. The held-out printer row is PS-261003-0417, ATTEMPT=2, ACK, RECOVER, bench. No historical model predicts every control, so **no target payload or K04 component is promoted**.

## Interpretation and boundary

This excludes only the enumerated one-step previous-payload hash/HMAC/BLAKE2 chain family with the specified source serial representations, metadata contexts, concatenation orders, and global pad/additive-offset forms. It does not establish that no stateful reducer exists, and it does not validate the recorded PS-0417 bytes. K04 remains unresolved; the official candidate and source files are unchanged.

A next K04 attempt should require a distinct source-bearing stage or a new complete-object model that predicts multiple untouched historical controls. Do not expand this into another generic hash or PRNG sweep. The original AX-7782 object, native ESC-N spool/coupon, or independently preserved commissioning record remains the decisive source route.
