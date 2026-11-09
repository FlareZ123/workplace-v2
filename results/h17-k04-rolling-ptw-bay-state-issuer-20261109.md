# K04: rolling four-bay PTW state as a printer coupon issuer

**Agent 1 | 9 November 2026. New complete-coupon construction; original K04 still missing.**

## Recovery idea

One alternative to the unverified copied 18:02 north printer ACK is that a printer job emits an escrow coupon from a *rolling four-bay register* of signed maintenance serials. Each of the 27 original PTW-390..416 records has one signed CLOSED/AS_LEFT serial in bay A, B, C or D; the printer spool independently preserves a complete same-suffix PS-0390..0416 ACK packet for every one of these 27 numbers. Each successive PTW record changes only its own bay's register. Once all four bays have appeared, the rolling state becomes a complete source-derived 16-byte coupon input for 22 intact PS jobs. The last PTW-417 signed/AS_LEFT set then provides a full 16-byte north coupon source without borrowing the disputed selected printer payload.

This **rolling historical state** differs from prior *single signed PTW serial → one printer word* affine/quadratic publisher models and from direct one-record hash issuers. The same-numeric-suffix PTW/PS relationship remains only a tested hypothesis: the original export provides no authorizing cross-reference.

## Frozen original controls and candidate construction

Use original SHA256-pinned maintenance/seal-receipts.jsonl and print/spool-reconstruction.log:

- Receipts: c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32.
- Printer: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.

At each PTW/PS suffix, take the latest **signed CLOSED/AS_LEFT** serial in each available bay. Full four-bay states first appear at job 0395. Use the first complete original source pair as a training observation; withhold all 21 later original full printer packets from every model fit. The selected PS-0417 copied ACK is excluded entirely.

Two original-informed bay orders (A/B/C/D and source field-sketch B/D/A/C), two per-word endian views, and three presentations (raw 16 bytes, pipe-joined bare hex labels, pipe-joined SG- labels) yield 12 candidate inputs. Frozen emitters include direct sixteen bytes, a shared unknown 16-byte XOR pad learned *only from the first authentic printer output*, and 41 MD5/SHA/SHA3/BLAKE2/HMAC first16-byte producer choices using original route constants and the six separately accepted slot bytes as possible keys. There are exactly **500 model assignments**.

A native-source synthetic register issuer with an unknown nonzero 16-byte pad recovers its hidden pad from one full source observation and correctly predicts all 21 withheld complete packets. This positive is a tool control, not historical evidence.

## Original results

| Measurement | Outcome |
| --- | ---: |
| Genuine cumulative four-bay / intact printer pairs | **22** |
| Entire original printer packets withheld from fitting | **21** |
| Historical complete models fitting every withheld packet | **0 / 500** |
| Synthetic hidden-pad complete source history | **PASS, 21 / 21** |

The highest signed/AS_LEFT PTW-417 revision in each bay yields source-state B/D/A/C:

D7DAD6BC9714519B7DAD0AD4BE8E87FD

Irrespective of failed historical controls, generate every complete 16-byte target value in the frozen family, with the official K04 XOR mask applied or omitted, and check the unchanged original K04 SHA256 commitment. The resulting **1,000 unique original component candidates yield zero PASS**.

**Reproducer:** [Agent 1 standard-library, original-source-pinned single-file SFT](../agents/agent1/k04_rolling_bay_state_issuer_sft.py). It leaves original evidence, acceptance, canonical candidate and verifier unchanged.

## Consequence

The rolling PTW register does construct an entire selected candidate without copying the corrupted 0417 ACK. Its tested direct/shared-pad/ordinary digest versions are incompatible with both the original intact historical heldouts and the original K04 commitment. This does not exclude an unknown printer postprocessor, different physical issue selection, or source data lost from the export; the numeric PTW/PS relation itself is unverified.

Do not use this rolling-state model as evidence of an original coupon. No K04 or K08 value was recovered. REC8/1 still has six accepted slots and two unresolved slots.

**Closest predecessors:** [single PTW-serial issuer screen](h17-k04-ptw-serial-to-spool-relation-screen-20261107.md), [per-bay quadratic source holdouts](h17-k04-ptw-bay-quadratic-word-publisher-20261107.md), and [PTW native donor transition](h17-k04-ptw-bay-transition-native-donor-sft-20261107.md).