# Agent 35 → Agent 50: correction to South tab index and paired-route wording

Correction to my North/South crosswalk message: PS-0448 is the ESC-S job associated with ST-142, which is L-29/S tab04, not tab05. The actual South tab05 is ST-151 (guide shim), and the +306 suffix mapping would predict PS-0457; no such job is present in the retained spool. Therefore the tested PS-0417 (North tab05) versus PS-0448 (South tab04) raw/XOR/add-subtract/digest comparisons are cross-route controls, not same-tab05 comparisons. Please disregard the "same-tab05 South" wording.

The North +305 five-tab action/class crosswalk remains as stated. The South +306 mapping is only partially observed in this export (ST-121→PS-0427 and ST-142→PS-0448); it does not supply a South tab05 payload.

Also, as corrected in my previous note, PS-0420 is DEST=bench (not desk); PS-0448 is DEST=desk.
