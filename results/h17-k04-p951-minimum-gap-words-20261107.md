# K04 p951: minimum eight-word acquisition set

**Status:** computational observability result under the existing source-only MT19937 printer model. The eight word values remain unavailable; no K04 component was recovered.

## Question

The p951 model leaves the selected 16-byte printer payload (128 bits) unconstrained after fitting the 132 intact packet payloads. The earlier gap-oracle work identified two candidate hidden-word regions:

- gap 43: stages 328–334 (7 complete 32-bit output words)
- gap 96: stages 721–728 (8 complete 32-bit output words)

All 15 words together determine the target. Neither region by itself does. The practical question is whether the records team must recover all 15 words.

## Method

Reused the exact source-only basis and stage alignment in `agents/agent49/k04_p951_symbolic_basis.py`:

- selected row 129 remains excluded;
- 132 intact 16-byte packet payloads are inserted as four little-endian 32-bit MT19937 outputs each;
- the resulting GF(2) coefficient rank is 15,365;
- the selected payload occupies stages 951–954.

For each candidate stage, treated its full 32-bit tempered output as 32 linear observations. Reduced the target and candidate forms modulo the existing printer-payload span, then exhaustively searched stage subsets by cardinality.

The search checked every subset of sizes 1–7 (16,383 subsets total) and every size-8 subset (6,435 subsets).

## Result

**Unique minimum: 8 full words.**

The unique smallest subset that makes all 128 target bits observable is:

| Gap | Required MT output stages | Count |
|---|---|---:|
| 43 | 328, 329, 330, 331 | 4 |
| 96 | 724, 725, 726, 727 | 4 |
| **Total** | **328–331 and 724–727** | **8** |

No subset of seven or fewer candidate words determines the selected payload. Exactly one eight-word subset succeeds. The remaining candidate words at stages 332–334 and 721–723, 728 are redundant for this target-observability calculation.

This is an acquisition reduction from 15 candidate words to 8. It does **not** identify which physical ticket field or attachment contains each word. The complete original ticket, underlay, attachment and index records should still be preserved so the stage-to-source mapping can be established without damaging provenance.

## Operational use

The eight observations must be the **32-bit tempered MT output values**, in this order:

1. gap 43: stages 328, 329, 330, 331;
2. gap 96: stages 724, 725, 726, 727.

Once these values are sourced, `agents/agent12/k04_p951_gap_word_recovery.py` uses the shared p951 model to reconstruct the selected 16-byte payload, XOR the K04 route mask, and verify the official K04 SHA-256 commitment. Inconsistent observations fail in the shared GF(2) basis; a recovered candidate is not accepted unless the commitment matches.

The ST-ticket offset remains unresolved. Under +300, the likely ticket locators for gaps 43/44/96 and selected job 0417 are ST-043/ST-044/ST-096/ST-117. Under the competing +304 hypothesis they are ST-039/ST-040/ST-092/ST-113. This minimum-word result is independent of that offset; use the authoritative `R:/Stores/returns/SEP26/index.htm` index or an original paired ticket to choose the correct records.

## Important limitation

The p951 basis is underdetermined by exactly the target 128 bits. A random or plausible 16-byte source block can be inserted as a mathematically consistent completion; consistency alone is not evidence. For example, the PTW-417 four-bay serial block can fill stages 951–954, but its post-mask candidate fails the K04 acceptance hash. The official commitment remains the final validation.

## Solver mechanics validation

`agents/agent12/test_k04_p951_gap_word_recovery.py` constructs one synthetic MT state consistent with the 132 intact printer packets, extracts the eight gap words and checks that the recovery function reconstructs the same synthetic target. The same recovery logic was exercised locally with a synthetic state consistent with the base printer equations, and it reconstructed that synthetic target. The committed test file provides a repository-side integration check; run it from the repository to verify the shared-module import path. Its synthetic target is not an archive value and is not expected to match the official K04 commitment.

## Reproduction

- `agents/agent12/k04_p951_gap_minimum_analysis.py` exhaustively reproduces the unique minimum subset.
- `agents/agent12/k04_p951_gap_word_recovery.py` consumes the eight sourced words and verifies K04.
- `agents/agent12/test_k04_p951_gap_word_recovery.py` tests the solver mechanics with synthetic, source-consistent values.

Both scripts reuse Agent49's source-only basis and make no changes to source evidence.
