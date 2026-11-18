# K08: eight-Emily-job AES-u16 and cross-note matrix screen

**Date:** 2026-11-18  
**Status:** bounded conjectural candidate family; no K08 recovery

## Question

Can the eight Emily-authored note jobs in the existing note-to-spool sequence crosswalk yield the exact K08 HMAC input by treating each 16-byte ACK payload as AES-128-ECB ciphertext under the published K08 desk nonce, then interpreting the decrypted block as eight unsigned 16-bit word offsets into the pinned 1889 *Falcon on the Baltic* text?

A second, source-indexed construction was tested: the five active phrase-source notes (N02, N06, N10, N13, N23) form rows of an 5×8 offset matrix; a common column, ordinal diagonal, or reverse diagonal yields one word per note.

This is a hypothesis, not a documented historical instruction. The desk nonce is not source-attested as an AES key, and the note-to-job sequence alignment is not a native queue manifest.

## Pinned inputs

- Original spool: SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Falcon word stream: 81,392 normalized words; joined-token SHA-256 excluding terminal LF `36997e8cf827a0c0ddade6104b8d63c5e462e69749653ce009e5e50ce4fcce66`.
- K08 desk nonce: `5F933DA6A1BD03C32DA5CBC25344F497`.
- K08 target commitment: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.
- The eight note/job rows are from `results/h17-k08-full-note-spool-sequence-crosswalk-20261118.md`:

| Note | Job | Class | Destination | Role |
|---|---|---|---|---|
| N02 | PS-261003-0302 | STORES | store | Emily note |
| N06 | PS-261003-0306 | RECOVER | desk | Emily note |
| N10 | PS-261003-0310 | STORES | store | Emily note |
| N13 | PS-261003-0313 | STORES | store | Emily note |
| N17 | PS-261003-0317 | LABEL | store | standby-label negative control |
| N18 | PS-261003-0318 | RECOVER | store | commissioning-label negative control |
| N20 | PS-261003-0320 | RECOVER | bench | earlier authoring-brief control |
| N23 | PS-261003-0323 | RECOVER | store | final-margin locator candidate |

## Method

1. Read the unique ACK payload for each of the eight mapped jobs from the pinned original spool.
2. Decrypt each 16-byte payload using AES-128-ECB with the K08 desk nonce as key, no padding.
3. Interpret the resulting 16 bytes as eight unsigned u16 offsets, using both big- and little-endian order and zero- and one-based indexing.
4. For each packet independently, take its eight indexed book words as an eight-word candidate phrase: 8 jobs × 2 byte orders × 2 bases = **32 candidates**.
5. For the cross-record test, exclude the three explicit controls N17/N18/N20. Across the five active note rows, test all eight common matrix columns, plus ordinal and reverse diagonals, under the same two byte orders and two bases: **40 candidates**.
6. Normalize each phrase according to the route (lowercase ASCII alphanumeric text, punctuation discarded, whitespace collapsed), compute HMAC-SHA256 with the desk nonce, truncate to 16 bytes, and SHA-256 that 16-byte result for comparison with the immutable K08 commitment.

The positive HMAC known-answer control, N02 draft phrase `a good watch leaves the room ready for the next pair of hands`, reproduced HMAC16 `BF889359B0303F2B2B2FD96AE841210B`.

## Results

<badge color="danger">0 / 72 commitment matches</badge>

All 72 complete candidate phrases failed the original K08 SHA-256 commitment. All unsigned u16 offsets were in range, but this is not discriminating: every unsigned 16-bit value is below 65,536, while the book contains 81,392 words.

The eight AES plaintext blocks were:

| Note/job | AES plaintext |
|---|---|
| N02 / 0302 | `3A89DB03A854613F81E0C430EDDB021F` |
| N06 / 0306 | `49FAA1956B31B80382D5B4C193F76C35` |
| N10 / 0310 | `23550A8D68C4F95D2A6CDB1DCF92B044` |
| N13 / 0313 | `DF10075F4E1D46DF161D2FE4B324C1F0` |
| N17 / 0317 | `2197F5356174A9FC2B6F33CCB873F6D8` |
| N18 / 0318 | `4EEA25CD74E9E2C90B7248D711219F93` |
| N20 / 0320 | `9266952F91A151BA399876EB5A0E83E2` |
| N23 / 0323 | `E5407654D33238607DFA324B94656E1D` |

The complete 72-phrase output, offsets, HMAC16 values, and slot digests are emitted by the reproducible script below.

## Interpretation and limits

- This closes only the finite AES-ECB / unsigned-u16 / whole-book and cross-note matrix constructions above.
- It does not establish that the 1889 Falcon transcription is David's physical book, that the note-to-job alignment is historically authentic, or that the desk nonce was used as an AES key.
- The matrix column/diagonal selector is conjectural; no source states that it is the intended selection rule.
- The separate byte-pair page/word interpretation remains untested because no pinned, edition-faithful page map for those coordinates is present. No new book fetch, proxy edition, or alternate offset system was introduced here.
- K08 remains **MISSING**. No candidate, acceptance commitment, route, or verifier was changed.

## Reproduction

Run from the repository root:

```bash
python agents/agent43/k08_eight_emily_aes_u16_sft.py
```

The script verifies the original spool SHA, pinned word-stream count and hash, N02 HMAC known-answer control, and the unchanged K08 target before printing all 72 candidate checks.

