# K04 PTW-to-printer packet-relative MT bridge falsification

**Date:** 2026-11-26  
**Identity:** Agent 50  
**Question:** Do the same-suffix PTW-390..416 seal serials occupy a fixed MT19937 stage relative to their corresponding PS-390..416 printer packets, and do the four PTW-417 serials occupy the four stages immediately before PS-0417?

## Result

No tested fixed-offset model survives the 27 same-suffix singleton pairs. Across offsets -16 through +16, both serial byte orders, and both raw-native-word and untempered-output interpretations, the best compatible prefix is only 3 of 27 before a contradiction. No complete 27-pair layout exists.

The natural four-bay target placement also fails: assigning PTW-417 serials in the K03 B,D,A,C order to MT stages 947..950, immediately before the PS-0417 packet start at stage 951, contradicts the existing printer-only MT equations under every tested byte-order and native/tempered interpretation.

**No K04 candidate is recovered.** The printer-only model remains underdetermined at the target (128 target bits unresolved); the PTW serials do not reduce that quotient under this fixed-offset model.

## Method

- Used the latest signed, CLOSED, AS_LEFT receipt for each singleton permit PTW-390 through PTW-416 and paired it by matching numeric suffix with PS-261003-0390 through PS-261003-0416.
- Reused the published packet-start stage map in `agents/agent49/k04_p951_symbolic_basis.py`. The target PS-0417 packet starts at stage 951.
- Rebuilt the base GF(2) MT19937 symbolic basis from the 132 intact printer packets, excluding selected row 129. Reproduction check: rank 15,365.
- For each singleton pair, placed its 32-bit serial at `STARTS[n-300] + d`, with d in [-16,16]. Tested big- and little-endian serial interpretation and both raw-native and untempered-output interpretations. Each layout was rejected on contradiction before all 27 serials could be inserted; the best prefix was three.
- Separately placed the four latest signed PTW-417 serials, in B,D,A,C order, at stages 947..950 and tested both byte orders and both native/tempered interpretations. All four variants contradicted the base basis.
- The K04 acceptance commitment and route mask were left unchanged. No PDF was opened or inspected.

## Interpretation and limit

This falsifies the specific model that the matching PTW serials are MT words at one fixed offset from their same-suffix printer packets, and the corresponding four-word pre-packet placement for PTW-417. It does not establish that PTW and PS records have no relationship of any kind, and it does not falsify unrelated generator or serialization models.

Do not repeat this fixed-offset scan or present the same-suffix join as a recovered K04 construction. A complete K04 recovery still requires a source-authenticated construction or original PS-0417 media/coupon evidence.
