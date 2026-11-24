# K04: AX-7782 attempt-1 checkpoint block under the four-fresh donor model

**Agent14 | 24 November 2026 | Bounded exploratory negative**

## Question

Can the eight pre-retry checkpoints for transfer AX-7782 provide a source-ordered four-word donor block for the existing all42/four-fresh printer MT model, yielding the missing K04 component?

This is a different source stream from the L-29/N supplier records. The AX-7782 transfer is for object `IR-261003-H17`, and its receipt occurs after the PS-0417 printer event. MAIL-13 says each chunk was retried once and the second attempt supplied the committed-chain checkpoint. The K07 source rule therefore selects attempt 2; attempt 1 is a real pre-retry record, but is not the accepted K07 input.

## Method

The reproducer is `agents/agent14/k04_ax7782_attempt1_fourfresh_donor_sft.py`. It:

1. Pins the print spool, transfer audit, MAIL-13, route and acceptance files by SHA-256.
2. Selects AX-7782 CHUNK records for attempt 1, orders them by sequence 0–7, and concatenates the eight 16-bit checkpoints into one 16-byte block.
3. Reuses Agent10's frozen `ALT_STAGES` / `GAP_DELTAS` four-fresh model, withholding the PS-0417 ACK2 payload exactly as the base model does. The source model rank is 15,434 and the target remains stage 955.
4. Tests only the source-fixed checkpoint order, with two donor starts (1409, 1863), two 32-bit word byte orders and native/tempered interpretations. No word permutations or selector expansion are used.
5. Converts each predicted coupon through the unchanged K04 XOR mask and checks the original K04 SHA-256 commitment. Candidate bytes are never printed.

## Result

- Presentations checked: **8**
- Distinct component candidates: **8**
- K04 commitment hits: **0**
- Source files changed: **no**

The test closes this one source-ordered attempt-1 block under the two donor starts and four word interpretations. It does not reject other possible transfer-system relationships.

## Interpretation and limitations

The attempt-1 block is temporally after PS-0417 and belongs to the same archive-transfer object, which makes it a plausible *exploratory* cross-stream input. There is nevertheless no source statement that the printer and transfer systems shared MT19937, or that the eight checkpoints were outputs at stages 1409 or 1863. Those starts are selected by observability in the mathematical model, not by a historical transfer-to-generator stage mapping.

The four-fresh inverse can map an arbitrary 128-bit donor block to a complete target because the selected 128-bit quotient remains free. Its inherited synthetic positive validates the algebraic inverse only. A hit would have been a candidate for further source authentication, not proof of historical provenance; the observed zero hit is a high-confidence negative for these eight fixed presentations only.

## Decision

Do not add attempt-1 permutations, alternate chunk pairings, or more AX-7782 donor presentations. The accepted attempt-2 checkpoint block was already in Agent10's original 11-block donor set; this result covers the only other source-authored attempt block for the same transfer. Further progress requires a documented shared producer/stage relation or the native AX-7782 object, not more arbitrary donor mappings.
