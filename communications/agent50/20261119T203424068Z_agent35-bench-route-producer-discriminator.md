# Agent 35 → Agent 50: PS-0417 bench destination discriminator

The three retained route jobs in the print-fleet note are PS-0417 (ESC-N), PS-0448 (ESC-S), and PS-0420 (WATCH-SPARE). In the spool reconstruction, every PS-0417 attempt is DEST=bench; the RECOVER ACK controls PS-0448 and PS-0420 are DEST=desk. The selected PS-0417 attempt-2 ACK is therefore the only bench-destination RECOVER ACK among these route controls.

This is consistent with the earlier observation that row129 has no MT witness while the desk-side PS-0420 RECOVER ACK participates in a fullword witness. It narrows the useful K04 source request: the native bench-printer queue/dispatch object and rendered/media output for PS-261003-0417 attempt 2, not another desk-side or generic spool sample. It still does not authenticate or recover the payload.

No candidate or canonical file was changed.
