# K04: node-50 recorder fields share the p951 MT stream (conditional)

**Date:** 2026-11-23  
**Status:** strong independent cross-carrier evidence for the p951 MT19937 source model; **not** a recovered K04 coupon.

## Executive finding

Using the existing p951 symbolic basis without refitting its 133 printer packet starts, a source-ordered subsequence of 20 node-50 recorder records is compatible with the same MT19937 stream. Each record contributes a 32-bit control word and a 13-bit auxiliary draw. The auxiliary values fit CPython-style `getrandbits(13)` rejection sampling, and the recorder's latch field independently agrees with a preceding `getrandbits(3)` draw for nearly all selected records.

The actual sequence order is highly informative: a dynamic program found a 20-record path with joint parity rank **599** and per-sequence stage gaps of 4–16. Across 1,000 random permutations of the 72 recorder sequence labels, the largest path had only **9 records / rank 228**. This is independent evidence supporting the p951 chronology, not proof of a documented common issuer.

Crucially, adding the recorder observations raises the p951 basis rank from **15,365 to 15,631**, but leaves all **128 selected ACK2 payload bits undetermined**. No K04 candidate or acceptance state changes.

## Pinned sources and method

- Printer source: `resources/evidence/print/spool-reconstruction.log`, SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Recorder source: `resources/evidence/recorder/trip-recorder.raw`, SHA-256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba` (2,128 bytes; 88 records total / 84 CRC-good; node 50 has 72 CRC-good records with sequence values 0–71).
- Existing source model: `agents/agent49/k04_p951_symbolic_basis.py`. Its 133 packet starts and selected row 129 at native stage 951 were reused unchanged; the selected payload remained omitted. The source-only printer basis has rank 15,365.

For each node-50 record and candidate control stage (s), the test:

1. Reads the control field as a little-endian 32-bit tempered MT output and untempers it.
2. Tests the 13-bit value `aux - 2000` against the top 13 bits of a tempered MT output at stage (s+d), (d in {1,2,3}).
3. Computes the **joint** independent parity constraints on the 32-bit control output and the 13-bit auxiliary output, rather than assuming the two sets of constraints are independent.
4. Searches for a source-sequence-ordered path with (4(j-i) le s_j-s_i le 16(j-i)), reusing the 4–16 draw envelope from the printer chronology. This envelope is a modelling assumption for the recorder, not a recorder-format guarantee.

The best path contains sequence values:

`7, 9, 10, 12, 13, 14, 24, 25, 39, 41, 42, 43, 44, 45, 54, 55, 61, 63, 64, 70`

Its joint ranks sum to **599**. A deterministic permutation test (Python seed `20261123`, 1,000 permutations of the 72 record assignments) had maximum path length **9** and maximum joint rank **228**, versus 20 / 599 in the actual sequence order. The same 1,000 permutation paths had at most 6 fully determined latch matches and at most 8 total compatible latch values, versus 11/12 fully determined and 19/20 compatible in the actual sequence path. This is an empirical permutation comparison, not a formal p-value for all possible source models.

## Emitter evidence

The auxiliary field is a 16-bit raw reading in the interval observed in the recorder. Treating it as (2000 + r), where (r=	exttt{getrandbits(13)}) and values above 6000 are rejected, gives exact source-model checks:

- Sequence 12: control stage (-775); the next draw at (-774) is fully determined as **7711** and is rejected; stage (-773) matches (r=5494), giving recorded auxiliary value **7494**.
- Sequence 39: control stage (-585); stage (-584) is fully determined as **7511** and is rejected; stage (-583) matches (r=1318), giving **3318**.
- Sequence 41: control stage (-568); stage (-567) is fully determined as **6630** and is rejected; stage (-566) matches (r=2823), giving **4823**.
- Sequence 7 is consistent with two rejections: stage (-809) is fully determined as **6635**; the next draw is not fully determined, but can exceed 6000; stage (-807) is compatible with (r=3899), giving **5899**. This last accepted-stage match has no independent parity constraints and is weaker than the three examples above.

The recorder latch values provide a separate check. At stage (s-1), the top three bits of the tempered MT output (the CPython `_randbelow(4)` / `getrandbits(3)` shape) are compatible with the recorded latch for **19 of the 20** path records. Eleven of those matches are fully determined by the original p951 basis; one record (sequence 61) is a mismatch and is not explained by this simple immediately-preceding-latch model. The other compatible cases add 22 independent bits when inserted into the basis.

## Linear effect on the selected coupon

- Adding the 20 joint control/aux observations increases rank by **244** (15,365 → 15,609).
- Adding compatible latch observations increases rank by a further **22** (→ 15,631).
- The selected PS-261003-0417 RECOVER / attempt-2 ACK payload remains **0/128 bits determined** at native stages 951–954. No complete component is produced and the original K04 SHA-256 commitment is not tested with a new candidate.

A rank-only extension shows that, **conditional on this exact p951 model and these recorder constraints**, adding consecutive future native output words from stages **1574–1971** (398 words) is sufficient to determine the 128 target bits. Five words at 1574–1578 are not sufficient. This is a model-specific sufficiency calculation; those future output values are not present in the surviving export.

The accepted K05 archive-latch group (node 49, event 82, sequences 300–303) does **not** match the p951 stream at any tested informative 32-bit phase from (-1100) through 2095. The recorder relationship found here is therefore not a licence to substitute the K05 component or to claim all recorder events share one generator.

## Interpretation and next evidence

This result materially strengthens the p951 chronology because it predicts structured values in an independent recorder carrier, including rejected auxiliary draws, without using the recorder fields to construct the printer basis. It remains conditional: the 4–16 recorder gap envelope and the stage assignments were inferred retrospectively; no source document states that node 50 and the printer share one CPython RNG instance.

The next useful source is not another broad PRNG sweep. Preserve the complete original recorder image and its sequence continuity, plus the original printer host spool/queue image or a later authenticated same-stream output tail. In the present affine model, the future output window 1574–1971 would resolve the target; the current recorder export and reconstructed spool log do not contain that window. A possible offset placing printer row 0 at global sequence 112 would leave sequences 72–111 unrepresented, but that offset is only one admissible alignment and is **not** established by the source.

The official candidate, commitments and verifier remain unchanged. K01/K02/K03/K05/K06/K07 remain the six previously accepted components; K04 and K08 remain missing; combined REC8/1 remains incomplete.
