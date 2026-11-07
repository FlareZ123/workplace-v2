# Node49 archive-latch snapshot delta as a K04 candidate

**Owner:** Agent 34  
**Date:** 2026-11-07  
**Status:** source-derived two-candidate family rejected; no K04 bytes recovered  
**Reproduction:** `python agents/agent34/k04_node49_snapshot_delta_sft.py`

## Question

The TRP2 recorder contains two complete, CRC-valid in-window snapshots for the archive-latch source (node 49, event 82): an earlier seq 200–203 snapshot and the K05-selected seq 300–303 snapshot. Could the per-latch change vector between these snapshots be the 16-byte K04 component or the opaque K04 payload?

This tests a complete state-transition object, distinct from using individual recorder words as PRNG donors or enumerating four-word donor permutations.

## Source reconstruction and positive control

The SFT pins the raw TRP2 file, format note, recovery-routing file and acceptance file. It parses the 16-byte header and 88 24-byte records, verifies each record CRC, and applies the official K05 window and per-latch greatest-sequence rule.

The K05 reducer selects seq **300, 301, 302, 303** for latches 0–3. Their preserved control bytes form:

`FF8B78200A56E8586DCDA00EF01E4572`

The SHA-256 of this exact 16-byte block matches the original K05 commitment. This is the positive control for record parsing, CRC handling, time-window handling, latch order and byte preservation.

The earlier complete in-window snapshot is seq **200, 201, 202, 203**:

`42BFD0538052760C6FC2B743BFB00270`

Its AUX values are 4312 per latch; the selected snapshot has AUX 4318 per latch. The later seq 900 series is excluded by CRC failures; seq 990–993 is outside the exclusive end of the K05 window.

## Candidate construction

For each latch, XOR its earlier seq-200-series control word with its K05-selected seq-300-series control word, preserving the four raw bytes and concatenating in latch order. This gives one 16-byte transition vector:

`BD34A8738A049E54020F174D4FAE4702`

Test it as:

1. the K04 component itself;
2. the K04 payload, followed by XOR with the official K04 mask.

The masked candidate is:

`386260B8EB4439ADA71D2D8A18B5A91E`

**Result: zero of two candidates match** the unchanged K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The disputed PS-0417 ACK2 payload is never read. No official source, candidate, acceptance file or verifier is modified.

## Interpretation and limits

This excludes exact reuse of the per-latch XOR transition from the earlier complete node49 snapshot to the K05-selected snapshot, either directly or as the payload before the official K04 mask. It does not establish a historical relationship between the recorder latch and the printer coupon, and it does not exclude other transforms or an independently retained native coupon.

This is a bounded source-grounded stop condition. Do not expand it into arbitrary latch permutations or cross-source XOR mosaics without a separate source rule. The next useful K04 evidence remains an independently authenticated original ESC-N coupon/native spool object or copy-stage integrity record. K08 is unaffected.

**Confidence:** high in the TRP2 reconstruction, K05 positive control and two-candidate exclusion; low in the historical relevance of the K05-to-K04 transition hypothesis.
