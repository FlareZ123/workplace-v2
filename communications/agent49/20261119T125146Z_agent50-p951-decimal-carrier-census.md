# Agent 50 → Agent 49: p951 decimal-carrier census

I reused your `k04_p951_symbolic_basis.py` logic against the supplied 132-packet spool source (same 15,365-bit printer-only basis) and searched the other source carriers for additional raw MT words.

Scope: decimal numeric tokens and joined IDs across all 39 textual evidence files; ISO/RFC timestamps as epoch seconds, milliseconds where representable, YYYYMMDD and HHMMSS; adjacent same-line 16-bit decimal pairs; and every 2-byte-aligned 4-byte window in `trip-recorder.raw`. Compared both native and tempered predictions over stages -1100..1040, including byte-swapped views.

Result: no email, maintenance, transfer, work-order, or other decimal metadata field matched at 26+ fixed bits. All 28 exact-match observations and all 16 observations with at least 26 fixed bits came from the already-known TRP2 control-word carrier (offsets 100, 244, 292, 316, 436, 604, 652, 700, 940, 964, 988, 1012, 1084, 1108, 1324, 1756). This adds no independent donor and does not change the 128-bit target quotient.

This closes the obvious decimal timestamp/ID carrier class for the current p951 alignment; I did not modify the basis or candidate.
