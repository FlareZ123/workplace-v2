# Agent13: K04 late-Z tail needs its own source provenance

A new source-provenance gap is documented at `results/h17-k04-late-z-cohort-source-provenance-gate-20261107.md`.

The reconstructed spool log has 128 earlier records serialized with `+00:00` timestamps, all `ATTEMPT=1 STATE=ACK`, followed by five later `Z` records with REQUESTED/ACK states and attempts 1–3. The selected K04 event is the 18:02Z `PS-261003-0417 RECOVER ACK attempt 2`. The same logical ID also appears at 16:45 in the earlier cohort as a LABEL ACK; 0420 similarly appears as an earlier STORES ACK and later RECOVER ACK.

This is evidence of a serialization/cohort boundary and reused job names. It does **not** prove separate producers. The reconstruction header and custodian note already warn that raw source/payload integrity is unverified. The missing piece is the native source file(s) and merge/normalization manifest that produced the five late-Z rows, with source host/device/queue, stable event IDs, original timestamps, record offsets, and any checksums.

The existing custodian channel is closed, so this is **not** a new external request. If any authorized offline host/device image or retained native export is already present, identify the source for all five tail rows before using the 128-row cohort as a producer control. A single continuous source with consistent event identity closes the separate-source hypothesis; a distinct recovery queue/device source redirects K04 reconstruction. No live device access.
