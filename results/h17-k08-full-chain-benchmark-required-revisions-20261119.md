# K08 full-chain benchmark: required pre-run revisions

**Reviewer:** Agent 43  
**Date:** 19 November 2026  
**Purpose:** pre-run specification review. This is not a benchmark result and does not recover K08.

The current [full-chain benchmark specification](h17-k08-full-chain-benchmark-spec-20261119.md) is a useful downstream factorial plan, but its 943,718,400 denominator is conditional on the chosen upstream route. Before execution or any full-chain claim, preserve the following source and representation distinctions.

## Required corrections

1. **State the scope of the denominator.** The current product `120 × 128 × 4 × 256 × 60 = 943,718,400` covers component order, global operators, transfer IDs, retry masks, and bookmark mappings. It does not by itself pass author/subset/row/splice/note-ID alternatives through the same endpoint. Either label its outputs conditional downstream, or evaluate a joint endpoint over upstream realizations. A practical factorization is to map each upstream realization to a canonical downstream-relevant signature (ordered components, K05 mask/output, K01 group/output, note/bookmark mapping, tokenizer, transfer-ID rendering), count multiplicities, and memoize downstream endpoint counts once per distinct signature. Do not multiply stage-specific rates or report a calibrated global p-value.

2. **Include the complete semantic source joins.** The source-local route is K05 lowpack `03 43` → `03C` → MAIL03 group C → K01 group-C selector 9 → MAIL09 tea-receipt / “map in the back” cue → Tea-room stock-sheet bookmark → reverse ordinal MAIL13. Report all 16 K05 latch masks (mask 15 remains the route-selected K05 source) and all K01 A/B/C/D group outputs under the same global operator. These are deterministic intermediates, not independent rarity factors.

3. **Freeze transfer-ID representation.** MAIL13 supplies the full hyphenated identifier `AX-7782`; it does not state that punctuation or the prefix should be discarded. Under ASCII-LSB packing: full `AX-7782` = 29 / 92; compact `AX7782` = 13 / 44; prefix `AX` = 1 / 2; suffix `7782` = 3 / 12 (reversed digits `2877` = 12 / 3). Compact `AX7782` can return directly to MAIL13 via selector 13; suffix `7782` can return through bookmark 3 → reverse MAIL13. These are distinct representation-dependent paths, not independent confirmations. Keep the full hyphenated ID as the source-exact baseline and report compact/prefix-suffix/suffix-only as controls. See [the reproducer and full four-ID table](h17-k08-transfer-id-rendering-sensitivity-20261119.md).

4. **Define the NOTE namespace over the actual source collection.** The note stack has N01–N24. For a 24-note reverse ordinal, position i maps to N(25−i), so bookmark 3 maps to N22. MAIL reverse remains 16−i, so bookmark 3 maps to MAIL13. Agent9 corrected the 60-row control and report; the benchmark specification should state these exact mappings rather than a generic NOTE namespace.

5. **Separate tokenizer dimensions.** Note bodies use a hyphen-preserving tokenizer in the existing decoder; routing/source strings use a hyphen-splitting tokenizer. The N20 contiguous-window control is 1,054 under the former and 1,096 under the latter; the same two positive hits survive. The 200,000 within-author note-order null is conditional on the hyphen-preserving note tokenizer unless the tokenizer choice is included in the upstream signature or a second null is run. The selected-note P212 prefilter itself survives this hyphen-tokenizer variation.

6. **Pre-register colon-label handling.** The P212 prefilter also strips each note-body prefix through the first colon. With this rule, selected note IDs [2,6,11,13,17,18,20,23] yield ATEALBIT, counts [13,11,14,22,8,5,30,21], NLOWIF?V, and N10 first token EVEN. Retaining full labels yields FSMASCIT, counts [19,14,16,22,11,8,30,21], TOQWLI?V, and N10 first token MUG; LOW IF EVEN disappears. Prefixes such as “First draft for the crew board:”, “Mug shelf:”, and “Standby envelope label:” plausibly function as field labels, but removal is a material extraction rule. Explicitly justify it as a body-field boundary and retain the full-label-preserving control.

7. **Keep P212 separate from committed K07.** K07 requires the greatest attempt per sequence; MAIL13 says attempt 2 supplies the committed checkpoint. The all-attempt-2 AX-7782 vector hashes to the accepted K07 value and LOW BIT packs to `53D5`. The P212 branch instead uses attempt 1 on even sequences and attempt 2 on odd sequences; its vector packs to `50D4` but does not hash to accepted K07. It may remain a separate, conditional K08 side-channel motivated by LOW IF EVEN, but it is not the committed transfer chain or an authenticated page/cell locator. The later P212 → MAIL04 → PTW-417 → N10 / TWRAP loop is downstream of the same mixed selector and is internal consistency, not independent validation. See [the attempt-selection conflict audit](h17-k08-p212-attempt-selection-conflict-20261119.md).

8. **Keep matched carrier controls in their proper scope.**
   - Complete email direct-adoption control: 20 EMLs, 560 raw / 482 unique normalized complete-text units, 0 HMAC hits; MIME walk confirms 20 text/plain leaf parts and zero attachments. This closes direct adoption and embedded attachments in the surviving email export only.
   - Surviving spool payload control: 133 unique 16-byte payloads; 266 forward/reversed raw SHA256 checks, 0 hits; 266 normalized forward/reversed hex candidates, 0 HMAC hits; zero printable-ASCII payloads. This closes surviving spool payload fields only, not missing native PS-0323 output/shadow/rendered objects.
   - Neither negative control excludes missing workbooks, photos, the physical book/receipt, or transformed multi-record constructions.

## Decision boundary

The P212 output is a locator hypothesis, not the K08 phrase. Its printed-page interpretation (page 212 in David's map-back book) and secondary Excel-cell interpretation (`mug-stock.xls!P212`) remain falsifiable but unverified. The physical tea receipt should be photographed in situ at printed page 212 before separation; the original mug-stock workbook should be checked at P212 only if supplied. The exact book title/edition and Emily's final envelope/margin are still absent.

K04 remains unresolved as well. The recovered BX25-08 property annex confirms FA-17 as the North office printer/cassette cabinet and strengthens the retrieval target: original L-29/N tab05 ST-112 R3/POSTED H17-POL-17/A3 docket, including both sides and any attached coupon/print strip. It contains no coupon bytes.

**No K08 phrase, K04 16-byte component, or complete REC8/1 recovery key is established by these findings.**
