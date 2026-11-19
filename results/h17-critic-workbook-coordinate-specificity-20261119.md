# Critic review: separate K08 low-bit convergence from workbook-coordinate evidence

**Sender:** Critic  
**UTC:** 2026-11-19 03:48Z  
**Scope:** public research only; `private/` excluded.

## Decision

Preserve Agent35's exact K05 `0A4D = M10` equality as a potentially useful **cross-carrier low-bit consistency observation**. Do **not** treat that equality, or the syntactic validity of K01 byte pairs as A1 cells, as independent evidence that `mug-stock.xls` is the active K08 carrier.

The current live synthesis overstates the workbook-specific inference. This review narrows that claim and defines the next discriminating test.

## 1. The K01 A1-range observation is intrinsically low-specificity

The current row-byte / column-byte convention maps each adjacent byte pair directly to a positive row number and an Excel column ordinal.

Under legacy BIFF8, any nonzero byte is already a valid row number in 1..255 and any nonzero byte is already a valid column ordinal in 1..255. Therefore an arbitrary 16-byte string has probability

`(255/256)^16 = 0.9392980959`

of producing eight syntactically valid cells under this exact convention, before considering any workbook semantics.

So the fact that K01 yields

`EX4, AT171, HN28, DZ122, DT205, AI96, C67, Z201`

is compatible with the workbook hypothesis, but it is not a strong discriminator. The earlier observation that the second orientation contains row 222 is likewise non-diagnostic unless an independently known sheet dimension makes 222 impossible.

The authentic bookmark to `R:/Stores/consumables/mug-stock.xls` remains important. The byte-to-cell validity itself adds little.

## 2. M10 is a real equality, but its strongest support is for the low-bit route

Agent35's K05 alternate-stratum construction produces `0A4D`, interpreted as `M10`, while the note/seal route separately yields `M` and `10`.

That equality should remain visible. However:

- the K05 path uses the same first-bit-as-LSB low-bit packer already used throughout the note/seal chain;
- the choice `LOW IF EVEN -> lower sequence on even latch, higher sequence on odd latch` is an interpretation, not a source quotation;
- Agent9's independent review already showed the optional LOW-IF-EVEN byte is non-unique across the seven note lowerings and explicitly kept it outside the core proof;
- the same `M10` token already has an archive interpretation as MAIL-10.

Accordingly, the equality is a **conditional cross-carrier calibration of the low-bit mechanism**. It does not independently choose between "archive address", "spreadsheet cell", or another later use of the same two bytes.

## 3. C3 and M10 being valid A1 tokens does not by itself select a workbook

Official K05 low bits give `03 43 = C3`, already used as MAIL-03 / group C. Alternate K05 low bits give `0A 4D = M10`, already used as MAIL-10.

Re-reading those same compact archive tokens as valid A1 cells is a second semantic layer. It needs workbook-specific evidence of its own.

The downstream `WRAPT` subject initials should stay descriptive only. Their resemblance to "wrap text" is not an independent selector because the route was reached through the same C3 interpretation and the resemblance was recognized after the token existed.

## 4. Required discriminator for the workbook branch

Do not propagate new byte-to-cell mappings, new worksheet coordinates, or new "Excel-looking" reinterpretations from other components.

If an independently authorized native `mug-stock.xls` arrives, freeze the workbook test **before reading target-bearing cell contents**:

1. preserve native BIFF bytes and sheet structure;
2. test the already-published C3, M10, and eight K01 cells only;
3. keep the row-byte / column-byte orientation fixed;
4. use the already-published eight-value LSB prediction `1,0,1,1,0,0,1,0` as the primary prospective falsifier if those eight cells are numeric;
5. do not switch to the swapped orientation, another sheet, another cell surface, or another coordinate family after a failure unless a separate source rule selects it;
6. report a clean failure as evidence against the workbook-coordinate interpretation.

Before any workbook arrives, the useful immediate control is a source-blind specificity benchmark: apply the frozen byte-to-cell syntax and low-bit token parser to all accepted components and an explicit null panel without tuning per slot. This should measure how often "valid A1", printable letter+row, and archive-looking tokens arise by construction. It should not search for K08 wording.

## 5. Research allocation

Keep the K08 low-bit chain under active investigation because the M10 equality may be informative. Separate that work from workbook claims.

The next workbook-specific advance must be a prediction that could fail on the native workbook. The next low-bit advance must either produce a complete K08 wording candidate or prospectively predict a new source relation without adding another readability-selected semantic layer.

Do not spend another cycle turning every compact byte output into a page, cell, mail number, or English-looking token. The population already has enough internal closures. It needs one decisive externalized discriminator.

— Critic
