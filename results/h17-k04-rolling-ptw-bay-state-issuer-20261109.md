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
## 9 November extension: native AES issuer with exact unknown copy-stage pad

The initial rolling four-bay source test excluded direct bytes, XOR pad and ordinary digest/HMAC issuers. A distinct, fully invertible 16-byte publisher is now checked: AES-128/ECB encryption or decryption of the accumulated PTW four-bay register under each of eight original, independently preserved 16-byte source keys (six accepted REC8 components, K04 mask and K08 nonce). An **unknown arbitrary 16-byte pad** is permitted on the input side or output side of AES, and recovered exactly from the first genuine intact PTW/PS source pair.

The source side tests bay order A/B/C/D versus B/D/A/C and four standard whole-word/word-byte views. The printer side independently tests those four packet views. This comprises **2 × 4 × 4 × 8 × 2 cipher directions × 2 pad stages = 1,024** complete modeled issuers. All models are fitted solely against original PTW-395/PS-0395; **21 other complete original printer packets** are withheld to test the issuer. The selected PS-0417 copied ACK bytes are never read.

Actual source execution:

- **0 / 1,024** exact whole-21-holdout fits.
- Every model fails **all 21 genuine intact printer heldout objects** (minimum total failed complete records = 21).
- Each model reconstructs a complete proposed PTW-417-selected 16-byte coupon and checks both direct stage and official route-mask stage: **2,048 distinct complete original K04 components, zero original full SHA256 commitment matches**.
- Four separate planted AES-producer simulations using real historical PTW input states, a hidden nonzero 128-bit pad, both AES directions and both pad stages: all source models recover the hidden pad, reproduce all 21 withheld whole emitted packets and decode a complete blinded PTW417 selected output.

This mechanism is more expressive than a simple known AES-key emitter, yet remains incompatible with the intact-source crosswalk in every tested version. The historical PTW/PS same-suffix relation remains unverified, and the negative does not rule out independent paper coupons or other unknown native printers.

**Reproducer:** [Agent 1 source-pinned AES rolling-bay SFT](../agents/agent1/k04_rolling_bay_aes_issuer_sft.py), Python with cryptography >=46.0. Source, original acceptance, candidate and verifier unchanged. It is a local completed source test, not a claimed independently completed CI action.

The original REC8/1 remains six slots accepted, K04 and K08 unresolved, combined INCOMPLETE.
