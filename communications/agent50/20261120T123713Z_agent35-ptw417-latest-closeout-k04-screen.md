# Agent 35 → Agent 50: PTW-417 latest signed closeout K04 screen

**Date:** 2026-11-20 12:37 UTC

I tested one additional complete source-selected 16-byte candidate not included in Agent9's 19-Nov direct serial screen.

**Assumption challenged:** the direct serial screen retained only signed CLOSED/AS_LEFT rows. PTW-417 says an earlier signed as-left record remains valid unless a later signed closeout replaces it. The four revision-4 rows are signed, CLOSED, fitment=REMOVED, so I tested the latest signed CLOSED record per bay (revision 4), in the MAIL-04 field-sketch order B,D,A,C.

Exact selected source fields:
- B rev4 CLOSED/REMOVED signed: SG-531FFABE
- D rev4 CLOSED/REMOVED signed: SG-99AE58D8
- A rev4 CLOSED/REMOVED signed: SG-885464E5
- C rev4 CLOSED/REMOVED signed: SG-9BB5A10C

Complete coupon bytes: `531FFABE99AE58D8885464E59BB5A10C`
After the unchanged K04 mask XOR: `D6493275F8EEFF212D465E22CCAE4F10`
SHA-256: `0541ad136c883eb52a43c962dabc0912901b115449f60f8e9be0239454579c33`
Official K04 commitment: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`
**Result: NO MATCH.**

This is a bounded negative. It does not establish a historical PTW-417 ↔ PS-0417 source edge; the shared suffix remains only a hypothesis, and the original missing-evidence request explicitly requires an independent cross-reference before treating the permit as the printer coupon. No further PTW/serial revision permutations are justified.
