# K04 unique-gap source-block pair screen

**Agent 43 — 12 November 2026.** A source-derived complete-candidate construction test using Agent 50's unique p951 gap pair. No K04 candidate passed acceptance.

## Question

Agent 50's p951 analysis identified one pair of four-word gaps, stages 328–331 and 724–727, whose 256 donor bits fully determine the withheld K04 printer payload at stages 951–954. Could those two missing blocks be copies of 16-byte records already present in other operational streams?

## Source blocks tested

Eleven distinct 16-byte blocks were constructed in source-defined order:

- WN-14 ink groups A/B/C/D (K01 source).
- LT-204 DIAG_WORD samples seq 0–7 (K02 source, 16-bit big-endian packing).
- PTW-417 selected as-left serial suffix words B/D/A/C (K03 source representation; this is a donor hypothesis, not the K03 ASCII prehash).
- TRP2 node49/event82 control words in latch order 0–3 (K05 source).
- RC-17 footer strips in service order for revisions B, C and D-draft.
- AX-7782 committed checkpoints seq 0–7, greatest attempt per seq (K07 source).
- PTW-417 revision-history blocks for revisions 1, 3 and 4, in B/D/A/C order. Revision 2 duplicates the selected K03 block and was deduplicated.

The constant repeated TRP2 auxiliary reading was not treated as a candidate block.

## Method

The SFT `agents/agent43/k04_unique_gap_source_block_pair_sft.py` imports the existing p951 symbolic source builder and keeps printer row 129 withheld. It maps each source block's four 4-byte words to one of the two unique gap blocks, preserving word order. For each block it tests the two ordinary byte orders and both native-word and tempered-output interpretations. Each distinct block pair is tested in both gap assignments.

This produces:

`11 choose 2 × 2 assignments × 4 interpretations per block × 4 interpretations per block = 1,760`

complete candidate constructions. The selected K04 payload, mask and acceptance commitment are not used to generate candidates; the mask and K04 slot hash are consulted only after each candidate payload is fixed.

## Result

All 1,760 models produced a fully determined 16-byte K04 payload. None of the resulting components matched the K04 acceptance commitment. There were no inconsistent or underdetermined models in this finite candidate set.

**No K04 bits were recovered.** The result rejects only the hypothesis that the two unique gap blocks are directly represented by a pair of the 11 tested source-derived 16-byte blocks under the tested byte-order and native/tempered interpretations. It does not exclude a different source block, a nontrivial transformation, or a different producer model.

Do not repeat this same pairwise source-block substitution screen. The next useful advance requires an independently authenticated original PS-0417 spool/coupon/copy-stage record or a genuinely different, source-supported construction. K08 remains dependent on the original final-margin, envelope, shelf-card or photograph-caption witness.
