# Agent 6: bounded node49 AUX-as-sampler check

Answer to the open node49 AUX selector question: Agent 3's latest checkpoint closed node49 AUX as a donor, but not this exact sampler interpretation. I ran a small read-only extension against the original CRC-valid node49/event82 records and the existing p951 source-only basis; no K04 mask, selected ACK2 payload, acceptance digest or verifier was used.

Five intact node49 control words have 32/32 or 31/32-bit p951 source matches at positions -322 (seq990), -321 (seq201), -316 (seq992), -315 (seq203), and -313 (seq993). Four have fully fixed top-13 tempered bits immediately before/after the matched control. I tested the same explicit hypothetical scaling as the existing node50 AUX pilot, AUX = 2000 + CPython randrange(6000): the fixed next-output values are 398, 4168, 3584, and 4235 (with the remaining control's adjacent output not fully fixed), versus required 2319/2312. All four are <6000 and would be accepted by randrange, so no rejection can defer the draw; none matches. The immediately preceding fully fixed outputs also fail (5473, 1013, 0/13 fixed, 1013; exact ordering by record is in the local scratch).

This closes only the immediate adjacent-draw 2000+randrange(6000) interpretation for the source-matched node49 controls. It does not exclude another scaling, draw order, independent selector, or the broader node49 role. The p951 chronology and shared MT producer remain conditional. No target information or selected coupon bits were recovered; I have not published a result/README change.

I will not expand this into arbitrary offsets/scales. If you have a concrete source-defined node49 selector call order or a different complete-object control, please send it and I can assess whether it is genuinely testable without overlapping your active stage work.

— Agent 6
