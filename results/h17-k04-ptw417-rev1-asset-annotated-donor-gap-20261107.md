# PTW-417 revision-1 asset-annotated donor gap

**Date:** 2026-11-07  
**Author:** Agent 11  
**Status:** source-structure finding; no K04 candidate.

## Source observation

The supplied seal-receipts.jsonl contains four PTW-417 revision-1 AS_LEFT/CLOSED/signed rows with both asset and inspector fields, one for each bay:

- A: SG-7E73B4CC
- B: SG-AD1D814B
- C: SG-5CB72EE5
- D: SG-64B2EE4A

MAIL-04 specifies the witness order B,D,A,C looking back from the access hatch. The resulting asset-annotated 16-byte block is:

`AD1D814B64B2EE4A7E73B4CC5CB72EE5`

A fifth PTW-417 revision-1 AS_LEFT/CLOSED/signed bay-A row, SG-574A9232, lacks both asset and inspector fields. The four extended rows form a complete asset-level set; the unannotated row remains a distinct source record whose relationship is unresolved. The original signed receipt, export lineage, row IDs, revision/void history and field-sketch/closeout correspondence are needed to determine whether it is separate, duplicated, superseded or a different physical item. A corpus-wide text search of the supplied archive found all five PTW-417 revision-1 serial tokens only in seal-receipts.jsonl; no other local file independently corroborates either bay-A serial or the extended set.

## Corpus coverage and bounded checks

The existing 533-carrier builder explicitly adds the latest signed AS_LEFT PTW-417 set (revision 2) as K03:selected. Its source-order and bay-sorted four-record sliding windows do not contain the complete revision-1 asset-annotated B,D,A,C block as a single carrier. The alternative revision-1 block using SG-574A9232 is also distinct.

Checks performed:
- Both revision-1 B,D,A,C blocks: direct SHA256-to-K04 and XOR-with-K04-mask SHA256, no match.
- Each revision-1 block paired with the selected K03 raw 16-byte donor under all 16 endianness/temper interpretations and both final high-bit choices in the two-donor inverse, no match.

Not performed: pairing the asset-annotated revision-1 block against every carrier in the 533-donor corpus in both operand positions. Agent 12 has been notified with the exact block and a suggestion for that narrowly scoped extension.

## Interpretation

This is a **donor-corpus coverage gap and source-provenance ambiguity**, not a K04 candidate. Preserve both bay-A rows and do not promote the asset-annotated block without the original signed receipt/field-sketch lineage. The permit/job number 417 overlap remains a separate possible cross-record link, not proof that PTW-417 serials supply K04.
