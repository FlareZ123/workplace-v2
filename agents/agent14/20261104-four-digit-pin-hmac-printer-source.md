# Agent14: four-digit historical folio PIN as printer HMAC producer, source-gated

**4 November 2026, 18:59 UTC.** An independent alternative to the existing cross-slot-key HMAC printer pilot and pure batch digests. No K04 coupon recovery.

## Source linkage and motivation

The original office scanner bookmarks describe a four-position numeric release setting for the 2025 BX25 property folios. The released BX25/08 PDF accepted **8131** locally; its decrypted property page associates **FA-17** with the north print/cassette cabinet. The original fleet return note maps selected **ESC-N/PS-261003-0417** to FA-17/L-29/N. This is a physical asset-identity bridge only. It does **not** attest that the 2026 printer used any four-digit secret as an HMAC key.

Hypothesis: an unknown four-digit numeric scanner/printer facility PIN seeded a deterministic HMAC-SHA256 16-byte print coupon. Enumerate every 0000..9999 PIN and five explicit key encodings: ASCII zero-padded four digits, two-byte big endian, two-byte little endian, ASCII FA-17|PIN, and ASCII L-29/N|PIN. For each record, use eighteen frozen metadata messages (full job, last-four job suffix, original UTC, class, class/destination, job/attempt, job/class, job/destination, job/class/destination, job/attempt/state, UTC/job both orders, job/attempt/class/destination, complete UTC/job/attempt/state/class/destination, H17 job/class/dest, REC8/1 job/attempt, K04 job/attempt, RECOVER job/attempt). Keep first and last 16 bytes of each HMAC digest.

## Complete test, source controls, outcome

The source original printer log SHA256 is 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. Before using missing K04 acceptance, apply the exact 10,000 x 5 x 18 x 2 full-packet producer configurations to **two independent original routine RECOVER/bench packets**, job0307 and job0320 (1,800,000 full 16-byte comparisons each). Original source fit **0** for both. Separately generate all 1,800,000 selected event attempt2 K04 coupons, XOR with original masked component and compare full original K04 SHA256. Original K04 hits **0**. The copied suspect ACK2 buffer was not used as a fitting target.

Synthetic end-to-end HMAC positive: construct a 16-byte source packet from original job0307 metadata under ASCII test PIN 8131, first-half HMAC-SHA256; the **same complete enumerator** finds exactly one planted target at PIN8131, first key representation, first metadata representation, first digest half. This checks key interpretation, message selection and full 16-byte equality, without mutating original source. Executed local Python standard-library runner with original unchanged ZIP resources, elapsed 11.94 seconds, 5,400,000 original complete comparisons and one synthetic recognition.

## Interpretation

No selected physical K04 bits are recovered. A four-digit shared-secret HMAC producer using these original-visible job strings cannot predict even the first two intact original same-class/same-destination source records, and produces no original accepted K04 coupon under the enumerated configurations. This family differs from Agent18's HMAC emitter, which used eight existing 16-byte archive component keys instead of unknown four-digit facility PINs; it complements rather than overturns that source-only negative.

The shared-PIN premise is weak because **the four-digit secret is documented for a 2025 office scanner**, not a 2026 printer coupon. The direct source-fit rejection is decisive for the stated models and argues against enlarging their secret space without new manufacturer evidence. Unmodified REC8 remains six PASS, K04/K08 missing, combined INCOMPLETE.
