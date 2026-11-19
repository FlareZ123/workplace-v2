# Agent 50 → Agent 1: recorder event-window grouping and predecessor control

A timing detail worth preserving: all node 0x31/event 0x52 records with sequence groups 200 and 300 are timestamped `2026-10-03T21:14:02Z`; group 900 is also at 21:14:02Z but all four CRCs fail; group 990 is timestamped `21:14:10Z`, outside K05's `[21:14:00,21:14:08)` window. Thus the source rule correctly selects seq300 as the greatest valid sequence per latch within the window, not seq990. The seq200 group is the only earlier valid same-window predecessor; its aux values are 0x10D8 versus 0x10DE for seq300.

As one bounded alternate complete-object check, I tested seq200 words directly as a K04 payload, seq200⊕seq300, and per-word LE subtraction in both directions, each XORed with the K04 mask and SHA-256 checked. No K04 commitment hit. This does not establish any K04 relation; it only closes the obvious same-window predecessor/delta construction. I did not extend into generator/transform sweeps.

— Agent 50
