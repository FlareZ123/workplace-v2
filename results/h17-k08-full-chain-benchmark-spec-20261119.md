# K08 full-chain benchmark — frozen specification

**Owner:** Agent35  
**Freeze date:** 2026-11-19 UTC  
**Status:** pre-run specification; do not change dimensions after inspecting joint endpoint counts

## Purpose

Produce one reproducible, source-pinned end-to-end sensitivity benchmark for the existing K08 locator chain. The stage-wise audits remain evidence inputs, not separate probabilities to multiply. The benchmark reports exact finite counts and matched controls; it does **not** produce a calibrated p-value or claim that a locator is the missing phrase.

## Immutable acceptance

- Read the six accepted component bytes from `candidate.json` and verify their SHA-256 commitments in `resources/acceptance.json`.
- Read the K08 target commitment and desk nonce from the unchanged acceptance/routing records.
- Verify source hashes for `recovery-routing.json`, `crew/noticeboard-and-desk-notes.txt`, `telemetry/freeze-export.jsonl`, `transfers/transfer-audit.jsonl`, `recorder/trip-recorder.raw`, `mail/13.eml`, and `retired-office-bookmarks.html`.
- Do not edit `candidate.json`, `verify.py`, acceptance data, or source records.

## Frozen upstream evidence and controls

1. **Author/subset selection:** retain the four encodings A0/A1 × LSB/MSB and the exhaustive 8-of-24 subset scan. Preserve every CREW4 hit, not just the selected one. Keep the existing conditional David-assignment null separate; do not multiply it into downstream frequencies.
2. **Row edits:** enumerate all valid +1 and -1 row shifts; report the source-selected N10→N11 +1 edit separately.
3. **ALOWBIT splice:** enumerate all 288 positional 1+3+3 splices. Record every hit and the exact head/middle/tail positions. The known duplicate caused by repeated A characters is counted as two configurations, not one independent observation.
4. **Note-order null:** retain the existing 200,000 within-author body-to-note-ID permutations, seed, and complete 16-condition predicate as a separate source-preserving matched control. Do not combine its rate with other stage rates.
5. **Complete-text test:** test full and post-label bodies of all 24 notes against the unchanged K08 HMAC; also retain the previously tested 22 direct-adoption candidates and the complete N13 candidate. No arbitrary phrase assembly from unrelated tokens.

## Frozen downstream configuration space

The downstream endpoint is evaluated over one global operator tuple, consistently applied to component extraction, source-map construction, transfer payload decoding, and transfer-ID suffix decoding:

- component half: upper / lower (2);
- source-byte bit plane: LSB / MSB (2);
- first-bit packing orientation: first bit has weight 1 / first bit has weight 128 (2);
- packed-byte order: forward / reverse (2);
- hex-character order: forward / reverse (2);
- character-bit weight order: first character has least-significant / most-significant weight (2);
- transfer-ID digit direction: forward / reverse (2).

There are **128 global operator tuples**. This explicitly separates source-byte bit-plane selection from bit-packing orientation. The earlier 16-way source-map scan called its LSB/MSB dimension `byte_bit_order`, but its implementation always selected `byte & 1`; that dimension was packing orientation, not source-byte bit-plane selection. The new benchmark must label and enumerate both dimensions distinctly.

For each global operator tuple:

- Enumerate all 120 ordered triples of the six accepted components.
- For each component, select the chosen upper/lower 8-byte half; select the chosen bit plane; pack with the global first-bit orientation to form the three-character component string.
- Report both endpoint definitions, without choosing after seeing results:
  - **literal endpoint:** case-insensitive text `YEA`;
  - **numeric endpoint:** selector value 7 from the low-bit character stream, weighted using the global character-bit order.
- Reconstruct K02 from the greatest GOOD/HOLD LT-204 DIAG_WORD revision per sequence in the K02 route window. Reconstruct K07 from AX-7782 attempt-2 chunks. Use K01, K05, K06 accepted bytes. Apply the same global source-byte bit plane, pack orientation, packed-byte order, hex-character order, and character-bit order to all five source-map inputs. The baseline map is exactly `K01=12, K02=11, K05=10, K06=10, K07=11`.
- For all four transfer IDs and all 256 retry masks, apply the same global operator to the 16-byte transfer vector. Decode the numeric ID suffix with the global character-bit order and the selected forward/reverse digit direction. Keep transfer ID and retry mask paired; never cross-pair a payload with another ID.
- Enumerate all 60 bookmark mappings: 15 positions × forward/reverse list direction × MAIL/NOTE namespace. Report the zero-based and one-based-with-offset forms as equivalent aliases, not independent mappings.
- The endpoint requires, on the **same global operator tuple and same transfer ID**, the selected component endpoint, the exact baseline source map, transfer selector 11, transfer-ID selector 3, and the tea-room bookmark mapping to MAIL-13. Count literal-YEA and numeric-selector-7 endpoints separately.
- Also report source-valid-mask-only endpoints (K07 mask 255), exact 53D5 endpoints, every selector frequency 0–15, and every per-transfer output frequency. Preserve equivalence classes where different operator tuples produce identical mappings or outputs.

The full downstream denominator is therefore:

`120 component orders × 128 global operator tuples × 4 transfer IDs × 256 retry masks × 60 bookmark mappings = 943,718,400 configurations.`

The benchmark must calculate the exact joint numerator by enumerating/factorizing these configurations while preserving the shared operator tuple and same-transfer-ID dependency. It must not multiply stage-specific probabilities or report the resulting ratio as a p-value.

## Matched controls to include in the same output

- K05: all 16 retained latch-retry masks, including the LOW IF EVEN selection.
- K07: all 256 retry masks for each of the four transfer IDs; identify mask 255 as the source-valid K07 mask.
- Bookmark loop: all 60 mappings and the two MAIL-13 mappings, distinguishing the tea-room bookmark.
- Note HMAC: 48 full/post-label checks (24 notes × 2 forms).
- Existing controls: N20 1,054 contiguous source windows; 19/20 email bodies reaching N13; 122/133 print payloads mapping to N01–N15 and 13/133 to N05; 200,000 within-author note-order permutations.
- Preserve source pins, deterministic row digests, random seed, sample count, and exact endpoint counts.

## Interpretation rules

- A matching selector or locator is not a recovered K08 component.
- The source-valid path and counterfactual alternatives must be labelled separately.
- Algebraically equivalent operator tuples count as separate raw configurations but one effective equivalence class; report both.
- No combined p-value, no multiplication of conditional nulls, and no post-hoc expansion of the frozen dimensions.
- A K08 recovery is claimed only if a complete candidate passes the unchanged HMAC commitment. A K04 recovery is claimed only if a complete 16-byte candidate passes the unchanged SHA-256 commitment.

## Independent challenge

Agent9 or Agent20 should challenge this specification **before** the joint endpoint enumeration is run. Any requested change must be documented as a spec revision before execution, not after seeing the joint counts.
