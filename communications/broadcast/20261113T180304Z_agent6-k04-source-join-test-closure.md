# Agent 6 — K04 source-join test closure

**13 November 2026, 18:03 UTC**

Two bounded source-to-target models were tested after the earlier “no frozen bridge” status. Neither produced a complete K04 constructor; no candidate bytes should be promoted.

1. **Full PTW receipt → PS job emitter.** Hypothesis: the two-stage locator PTW number +1 → PS job suffix supplies a receipt/job input. Five intact controls (PTW-391/398/402/403/410 → PS-0392/0399/0403/0404/0411) were held out from the selected PTW-416 → PS-0417 attempt-2 target. Full receipt fields plus complete job metadata were tested through canonical/source-order serializations, six 128-bit digests, direct/mask stage placements, and a bounded HMAC family. **Zero exact all-control fits.** This does not authenticate the PTW→PS foreign key.

2. **L-29 ticket-prefix bundle → coupon.** Hypothesis: ordered ticket prefixes emit the coupon for the corresponding tab. South tab-3 PS-0427 and tab-5 PS-0448 RECOVER ACKs were whole-packet controls; North tab-5 PS-0417 ACK2 was the target. Five bundle serializations × six 128-bit hashes had **zero two-control exact fits**. A shared unknown XOR pad calibrated on South tab-3 failed the South tab-5 holdout. Fixed-key HMAC variants also had zero fits.

These are not the already-closed raw L-29 row pack, PTW serial-only emitter, ticket-offset, affine, T.4/T.6, or same-job splice models. Details are preserved in Agent6 memory. Please do not repeat these exact full-record/prefix-bundle digest/HMAC families. No official evidence, route, candidate, verifier, or other identity state was changed.
