# K08 factorized full-chain endpoint audit

**Agent35 — 19 November 2026**

**Status:** exact finite sensitivity audit completed. No K08 phrase recovered; no candidate, verifier, acceptance, or source file changed.

## Question and scope

Does the observed K08 route close to MAIL13 when the same global operator tuple is applied consistently to component extraction, the five-input source map, transfer-payload decoding, and transfer-ID decoding, while preserving the transfer-ID-to-bookmark dependency?

This audit uses the six already accepted component values and the source-selected note signature. It does not claim a calibrated probability. The downstream Cartesian space is enumerated exactly by factorization rather than materialized.

Reproduce from the repository root:

    python agents/agent35/k08_factorized_full_chain_joint.py --out results/h17-k08-factorized-full-chain-joint-20261119.json

The standard-library script pins the acceptance file, routing, telemetry, transfer audit, recorder, note file, bookmark page, and MAIL03/06/09/13. It reconstructs K02, K05, and K07 from their source records and checks the six accepted component commitments before counting anything.

## Upstream signature and multiplicity

The exhaustive CREW4 scan covers 4 × C(24,8) = 2,941,884 encoding/subset pairs and finds two CREW4 subsets:

- A0_LSB: N02, N06, N11, N13, N17, N18, N20, N23
- A0_MSB: N02, N06, N11, N13, N17, N18, N20, N23

Each hit has seven valid adjacent +1 edits and seven valid adjacent -1 edits. Only the A0_LSB, N10 → N11 edit produces ATEALBIT. Across all 288 head/count/head splice positions, ALOWBIT occurs twice, at head positions 0 and 3. These are two encodings of the same selected note set and the same downstream signature—not two independent downstream observations.

The selected component order is therefore K01, K06, K02 (A / LOW / BIT → 1 / 6 / 2).

The note parser uses the body after the caption/type prefix. Preserving the Caption: / Mug shelf: / Workshop card: prefixes is a different parser and breaks the bridge. The source-window control and the 200,000-trial within-author note-order null are separate upstream controls; neither is multiplied into the downstream denominator.

## Source joins: WN-14, K05, and MAIL03/06

MAIL03 and MAIL06 jointly reproduce all four WN-14 K01 groups, byte-for-byte:

| Group | Source bytes | LOW BIT group selector |
|---|---|---:|
| A | 049AAB2E | 4 |
| B | 1CDE7A82 | 0 |
| C | CD7C6023 | 9 |
| D | 4303C91A | 7 |

The retired standby transcription's group-D value ending 5E67 is not the accepted WN-14 group D.

For K05, the source-selected greatest-sequence choice is mask 15. Under source-byte bit plane LSB and first-bit packing LSB, mask 15 packs to 03 43 (03C); the note-derived LOW IF EVEN mask-10 control packs to 0A 4D. All 16 masks are retained in the reproducer output.

The MAIL03/06 source join, K01 group-C selector 9, and K05 03 43 intermediate agree under every global operator that reproduces the five-input source map.

## Globally coupled downstream space

The seven operator dimensions are:

1. component half: upper / lower;
2. source-byte bit plane: bit 0 / bit 7;
3. first-bit packing orientation: LSB / MSB;
4. packed-byte order: forward / reverse;
5. rendered hex-character order: forward / reverse;
6. character-bit weight: LSB / MSB;
7. numeric transfer-ID suffix direction: forward / reverse.

This gives 128 global tuples. The same tuple is used across all relevant stages; the transfer ID is never paired with a different transfer's payload.

The exact downstream denominator is:

    128 operators × 120 ordered component triples × 4 transfer IDs × 256 retry masks × 60 bookmark mappings = 943,718,400.

Eight tuples (indices 0, 1, 6, 7, 64, 65, 70, 71) reproduce the exact source-map vector:

    K01=12, K02=11, K05=10, K06=10, K07=11.

All eight also preserve K01 group C = 9 and the K05 mask-15 03 43 intermediate. They share source bit plane 0, first-bit packing LSB, and forward packed-byte order. The two equivalent source-map renderings are forward hex with LSB character weighting, or reversed hex with MSB character weighting. The upper/lower component half and transfer-ID digit direction account for the remaining multiplicity.

For the source-selected component order K01, K06, K02:

- upper half packs to bytes 04 83 F9, selector 6;
- lower half renders yEa, selector 7.

Across all 120 component-order alternatives, the numeric selector-7 counts are 60/120 for upper and 24/120 for lower. Literal YEA occurs 0/120 for upper and 1/120 for lower. Thus the observed order reaches literal YEA only in the lower-half branch.

For source-valid AX-7782, mask-255 transfer payload, the decoded payload is 53D5 (or 5D35 under the equivalent reversed-hex representation) and returns selector 11 under all eight source-map-matching tuples. Across all 256 masks, selector 11 occurs 64 times for AX-7782 and 72 times for AX-7781; it occurs zero times for AX-7778 and AX-7783. Only AX-7782/mask 255 is the source-selected transfer.

## Transfer-ID and bookmark boundary

MAIL13 supplies the full identifier AX-7782. Its LOW BIT values are:

| Rendering | Character weight LSB | Character weight MSB |
|---|---:|---:|
| Full AX-7782 | 29 | 92 |
| Compact AX7782 | 13 | 44 |
| Prefix AX | 1 | 2 |
| Numeric suffix 7782 | 3 | 12 |
| Reversed suffix 2877 | 12 | 3 |
| Full with reversed digits AX-2877 | 101 | 83 |
| Compact with reversed digits AX2877 | 49 | 35 |

The full source identifier therefore does not return bookmark position 3 or 13. It cannot reach the 1–15 bookmark domain as a single string.

The 60 bookmark mappings are 15 positions × two directions × two namespaces. The namespace arithmetic is kept distinct:

- reverse MAIL position 3 → MAIL13;
- reverse NOTE position 3 → N22 (not N13);
- forward MAIL position 13 → MAIL13, whose bookmark title is Blank request form;
- the Tea-room stock sheets browser bookmark is position 3.

MAIL09 mentions a physical tea receipt used as a bookmark and says the map in the back belongs to David. That physical receipt and the browser's Tea-room stock sheets bookmark are distinct objects in the export; connecting them is an inference, not an identity established by the files. “Map in the back” may motivate reverse order, but does not itself specify a browser-bookmark namespace or direction.

Two alternative renderings can create self-returns to MAIL13:

- **Suffix-only control:** 7782 → 3, then reverse MAIL bookmark position 3 → MAIL13 (Tea-room stock sheets).
- **Compact-ID control:** AX7782 → 13, then forward MAIL bookmark position 13 → MAIL13 (Blank request form).

Neither is the full source identifier as written. MAIL13 does not state that its prefix/hyphen should be discarded, nor that one of these two bookmark mappings is intended.

## Exact factorized endpoint counts

The following are counts over the full 943,718,400-case downstream space, conditional on the observed upstream signature and the source-map/K05/K01 gates. They are finite enumeration counts, not p-values.

| Endpoint | Numeric selector 7 | Literal YEA |
|---|---:|---:|
| Full source ID + tea bookmark → MAIL13 | **0** | **0** |
| Suffix-only ID + reverse tea bookmark → MAIL13 | 10,752 | 128 |
| Compact ID + any MAIL13 bookmark mapping | 10,752 | 128 |
| Suffix-only + source-valid AX-7782/mask-255 only | 168 | 2 |
| Compact ID + source-valid AX-7782/mask-255 only | 168 | 2 |

The source-selected component order and source-valid transfer mask give two global tuples that close the suffix-only tea-bookmark path with literal YEA; the full source ID gives none. The compact-ID path also has two lower-half tuples for the observed order, but it uses the unrelated forward position-13 bookmark.

The factorization preserves the same global operator and the same transfer ID throughout. It does not cross-pair a selector from one transfer with another transfer's payload. The 943,718,400 denominator is conditional on the single observed upstream signature; do not multiply it by the separate CREW4, note-order, or source-window null rates.

## Separate upstream/carrier controls

These remain separate controls, not factors in the downstream denominator:

- The existing within-author note-order null tests 200,000 permutations across four seeds (20261119–20261122) and finds 0 full-upstream-chain hits; the possible within-author permutation space is 1,254,113,280. See results/h17-k08-note-order-null-20261119.json.
- The N20 source-window control has 1,054 valid windows under hyphen-preserving tokenization and 1,096 under hyphen splitting. The same two positive windows survive: MAIL11 long watch with → selectors 10/11/3 → N20 end of the; routing rule late watch rather → 10/11/18 → the same N20 words.
- The full-label-preserving note control changes 18/24 HMAC selectors and all 24 paths terminate at selector 0; the body-field parser is the viable source-field interpretation.
- The all-20-email MIME inventory finds one text/plain leaf and no attachments per message. The separate complete-email direct-adoption search reports 560 raw / 482 unique spans and zero exact K08 HMAC hits.
- The separate spool-payload control reports 133 unique non-printable payloads, with no exact K08 HMAC hit under its tested forward/reverse and hex-rendered controls.

These controls narrow the source route but do not provide the missing K08 wording.

## Conclusion and next work

The source-supported chain reaches a precise locator signature: the selected notes, WN-14 groups, K05 intermediate, component order, and AX-7782/mask-255 payload selector all reproduce. The last return to MAIL13 is representation-dependent. With MAIL13's full identifier, the tea-bookmark endpoint is zero. Suffix-only and compact-ID returns are useful hypotheses, not authenticated parsing rules.

This audit does not recover the final K08 caption, and it does not resolve K04. No candidate slot or acceptance artifact was changed.

Next work should avoid another broad permutation or Cartesian rerun. The valuable open question is whether any source record authorizes the suffix-only or compact-ID parse, or whether a different source-backed authoring route connects the final N23 envelope wording to an extant artifact. Preserve the two alternative return paths as explicit controls; do not promote either to fact without a source witness.
