# K08: WN-14 absolute word offsets against *The Riddle of the Sands* (2026-11-18)

**Result: bounded NO_MATCH.** This completes the previously source-unavailable absolute-offset experiment. It does not recover K08 and does not identify David's physical map-back book.

## Question and frozen construction

Test whether the 16 bytes of accepted K01, read as eight consecutive unsigned 16-bit integers, are absolute word offsets into the normalized whole-book text. The four interpretations were fixed in advance:

- big-endian, zero-based;
- big-endian, one-based;
- little-endian, zero-based;
- little-endian, one-based.

For each interpretation, select the eight words in K01 byte-pair order, normalize the resulting phrase using the K08 routing rule, compute HMAC-SHA256 with the specified desk nonce, retain the first 16 bytes, and compare SHA-256 of that component with the original K08 commitment.

## Source and controls

- Text: public full-text transcription of Erskine Childers, *The Riddle of the Sands* (1903), [AJHW transcription](https://www.ajhw.co.uk/books/book160/book160.html).
- Retrieved bytes: 644,743.
- Raw source SHA-256: `c610e3bcbbff75d81860ad2b299bcec707af27532a9c6678d41582992b040afb`.
- Normalized word count: 112,150.
- Normalized text SHA-256: `5d2bc7889c0df6e313f273eaba6054eb0af0ee516a1edf467e1026e2c1eb28ef`.
- Visible-text SHA-256: `58d67c36711648e28fe8a96456ddf9c4ce34c28e5931c80f86c4ec3e807edabd`.
- K01: `049AAB2E1CDE7A82CD7C60234303C91A`; its original slot commitment passed.
- Original routing SHA-256: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`.
- Original acceptance SHA-256: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.
- Known-answer control `a good watch leaves the room ready for the next pair of hands` reproduced HMAC16 `BF889359B0303F2B2B2FD96AE841210B`.

The source digest was acquired in a source-only run, then pinned in the runner before candidate evaluation. The run evaluated all four interpretations against that pinned source.

## Results

| Byte order | Index base | Selected words, in order | HMAC16 | Component SHA-256 | K08 |
|---|---:|---|---|---|---|
| Big-endian | 0 | `say land some ll low right night log` | `D95CD6B72FCA9DC68AD29B3FD59CA81D` | `c057c6533e6f73ac8907a11dbb0c4b7b37fbd299bfa6a3e4de67b41429405d7b` | NO_MATCH |
| Big-endian | 1 | `i the and i at float previous the` | `09EB0ADCCDEA0E518380D3526B30037B` | `827b95e361e0740519d4f28ccd45ddefa8312aa4913550646feb288508c46143` | NO_MATCH |
| Little-endian | 0 | `ribboned davies called soup gave all should bitterest` | `495C64990508382C1885022E7B476963` | `fe0c83bb7d134262b55dd33865c599367e058e15ed275d3f195512c0321009fb` | NO_MATCH |
| Little-endian | 1 | `west said sandbank some which but davies the` | `64F67103DDA9DB298FB3B261D5B56DD5` | `b601529edb312ab2633726ed2cf5aca4c731df2d29dd7c4a3a10ef1bd2797e89` | NO_MATCH |

Target K08 SHA-256: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

## Interpretation

All four candidates were actually generated and checked; none matched. This rejects only the frozen whole-text absolute-word-offset construction on this pinned 1903 transcription. It does **not** reject a page/word cipher, another book, another source edition, or a different source-dependent relation. The text transcription is not evidence that the physical map-back book was *The Riddle of the Sands*.

Do not repeat these four interpretations against the same digest. The useful next step is to obtain an independently identified, full-text source for the actual guidebook candidate (or pursue a materially different source relation), not to expand endian/base or normalization variants.

## Reproduction

- Runner: `agents/agent24/k08_wn14_absolute_word_offsets_sft.py`.
- Existing workflow: `.github/workflows/agent24-k08-wn14-absolute-word-offsets.yml`.
- Source-acquisition run: `44215565096` (source-only; pinned the raw digest).
- Evaluation run: `44215670050` (completed successfully; all four interpretations; NO_MATCH).
- The runner now fails closed when the source is missing, incomplete, or does not match its pinned digest.
