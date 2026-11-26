# Agent 4 — complete-export source-surface pilots (2026-11-26)

## Purpose

After reading the current Critic broadcast and the existing K04/K08 prior art, I tested two narrow source-surface gaps rather than extending the existing PRNG, phrase-grammar, or generic checksum sweeps. These are negative results; no candidate component was changed.

## K04 — bit-stuffed HDLC/T.30 frame-body hypothesis

**Source cue:** crew note N22 remarks that the label printer had been behaving like a fax machine. This is an informal observation, not evidence that the printer actually emitted T.30 frames.

**Distinct question:** could one retained 16-byte payload be a bit-stuffed HDLC/T.30 frame body whose FCS is CRC-16/X-25, rather than a plain 14-byte body followed by two FCS bytes?

The source-pinned test in [`agents/agent4/k04_t30_hdlc_fcs_sft.py`](../agents/agent4/k04_t30_hdlc_fcs_sft.py) checks all 133 retained payload rows in both raw and route-mask-XOR views. For each view it tries MSB-first and LSB-first bit order, normal and inverted polarity, all eight bit offsets, and up to seven trailing pad bits, then destuffs and validates the X.25 FCS. This is 68,096 decode configurations. A synthetic positive control containing one stuffed bit and seven pad bits is recovered exactly.

**Result:** zero valid FCS-bearing frame-body decodes across the retained rows. The selected `PS-261003-0417` attempt-2 `ACK/RECOVER` row contains no `0x7E` flag occurrence in either bit order, before or after the route-mask XOR. The selected K04 commitment-match count is zero.

**Boundary:** this rejects only a complete bit-stuffed FCS-bearing body contained in one retained 16-byte payload under the tested views. It does not reject a native `.SPL/.SHD` object with framing removed, a frame split across records, or another printer protocol. The N22 remark alone is not enough to justify a broader fax-protocol search.

## K08 — literal phrase scan over every accessible non-PDF export member

The earlier shared-phrase scan covered the desk notes, emails, and galley log. This extension checks whether the final normalized phrase appears literally in any other accessible text-bearing field in the supplied export.

The source-pinned test in [`agents/agent4/k08_all_export_literal_scan.py`](../agents/agent4/k08_all_export_literal_scan.py) scans all 45 non-PDF members. It extracts EML headers and bodies, HTML text and selected attributes, JSON keys and string values, CSV rows and cells, plain-text lines and paragraphs, and printable ASCII runs from the recorder binary. It also checks each whole field and every contiguous normalized word span up to 48 words. The official K08 nonce and commitment are loaded from the source files at runtime and are not printed. Normalization and HMAC implementation controls pass.

- 4,711 extracted text fields
- 717,768 unique normalized phrase candidates
- Non-PDF member-manifest SHA-256: `225fa828826041fc2dd805ed5055b466a09666dbe32dc7c7f13f546aadba14e3`
- K08 commitment matches: **0**

`BX25-08.pdf` was excluded before reading its contents; no PDF content or PDF-derived values were used.

**Boundary:** this rules out a literal contiguous phrase in the accessible non-PDF export text under the specified normalization and 48-word span bound. It does not rule out a phrase assembled from non-contiguous fields, a binary-encoded caption, a phrase in an absent photo/envelope/desk artifact, or any PDF-derived material.

## Research consequence

Neither test recovers K04 or K08. The six already accepted components remain unchanged; the complete recovery key is still unverified. No `candidate.json`, acceptance commitment, verifier, or source evidence was modified.

The next useful K04 evidence is still the authorized original PS-0417 native spool/coupon or an authenticated printer-media export. The next useful K08 evidence is the original final envelope face/underlay, photograph caption, or keeper-desk artifact. Without one of those carriers or a new source-authored producer rule, expanding generic fax/CRC or phrase-generation families would repeat prior work rather than materially improve recovery.

## Reproduction

From the repository root:

```bash
python agents/agent4/k04_t30_hdlc_fcs_sft.py
python agents/agent4/k08_all_export_literal_scan.py
```

Both scripts default to `resources/`, pin their inputs, emit only aggregate results, and are read-only.
