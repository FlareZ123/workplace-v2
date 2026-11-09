# K04: source-relative AES printer issuer with complete watch ACK withheld

**Agent 5 | 9 November 2026 | Original-source experiment: no K04 match.**

## Proposed complete-coupon construction

The untouched print export preserves three different RECOVER ACK jobs:

- South ESC-S, PS-0448 ACK1 at 18:24: complete copied payload `234BE186E97EE05830909790E336109E`.
- Watch WATCH-SPARE, PS-0420 ACK2 at 18:25: complete copied payload `432475F72A62DB39F3D5693E2C937FA4`.
- North ESC-N, PS-0417 ACK2 at 18:02: copied payload excluded from this candidate construction, since its selected physical integrity is in dispute.

**Alternative stage model:** An unknown common 16-byte copier/export pad is XORed with AES-128 encryption or decryption of a source-derived per-job metadata block, under one of the six already accepted archive keys, the original route mask, or the K08 nonce. This is a speculative device producer: no original record authenticates AES or a common pad.

For each exact source-model assignment, recover the common pad from the entire South ACK object, use it to predict the entire **withheld original Watch ACK** without reading that object's bytes during fitting, then predict the North coupon and apply the unchanged K04 route mask. The K04 copied ACK2 payload is never consulted as a coupon donor. This relative model changes the stage interpretation versus the prior absolute AES issuer and differs from the recently published HMAC-based three-route pad model.

Metadata layouts: 13 source-visible job/time/class/destination strings, each represented six ways (MD5, two SHA256 halves, BLAKE2s-128, and two 16-byte raw/padded views), plus five numeric fields in four 16-byte representations. Four word/byte presentations and AES encryption/decryption are frozen. Total 8 × 98 × 4 × 2 = **6,272** whole-model assignments.

## Executed original result

The [portable SFT](../agents/agent5/k04_aes_relative_stage_sft.py) ran against the supplied original 46-file ZIP extracted unchanged into a local checkout-equivalent tree. It checks the full printer SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, exact route mask, original K04 SHA256, the six individual accepted components and both historical whole ACK control bytes.

| Result | Count |
| --- | ---: |
| Complete original-source model assignments | **6,272** |
| Distinct complete K04 component candidates | **5,089** |
| Exact withheld Watch ACK predictions | **0** |
| Original full SHA256 K04 hits | **0** |
| Planted South/Watch/North whole-packet calibration checks | **6,272 PASS** |

In the planted tests, each model's AES emitter is wrapped with an independent fixed hidden 16-byte pad. Calibration using only the synthetic South ACK recovers the pad, and the synthetic Watch and North full 16-byte outputs are recovered exactly.

**Interpretation:** This exact known-key AES + shared-pad producer family fails the independent Watch control and does not recover K04. The preserved South and Watch spool values themselves have no independent physical-copy authentication, so the source-only failure is limited to the copied-file stage. No coupon bits are authenticated; no K08 caption words are recovered. Six accepted slots remain valid, with K04/K08 and combined REC8/1 still unresolved.

The original evidence, acceptance commitments, canonical candidate and verifier were not modified. Expand only if a source-derived AES key/pad or issuer-stage relation warrants a genuinely different construction.
