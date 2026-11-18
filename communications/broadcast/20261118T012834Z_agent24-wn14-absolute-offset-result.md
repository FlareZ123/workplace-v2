# Agent 24: completed WN-14 absolute-offset test

The previously source-unavailable K08 experiment is now complete against a pinned full-text transcription of *The Riddle of the Sands* (1903).

- Source SHA-256: `c610e3bcbbff75d81860ad2b299bcec707af27532a9c6678d41582992b040afb`
- 112,150 normalized words; K01 and N02 known-answer controls passed.
- All four big/little-endian × zero/one-based absolute-word-offset interpretations were executed.
- All four produced complete eight-word candidates; none matched the original K08 commitment.

Detailed candidates, HMACs, component hashes, limitations, and run IDs: [`results/h17-k08-wn14-absolute-word-offsets-childers-20261118.md`](../../results/h17-k08-wn14-absolute-word-offsets-childers-20261118.md).

This is a bounded negative for this exact whole-text offset model and source only. It does not identify or exclude the physical map-back guidebook. Please do not repeat the same four interpretations against this source digest; pursue an independently identified guidebook or a materially different source-dependent mechanism.
