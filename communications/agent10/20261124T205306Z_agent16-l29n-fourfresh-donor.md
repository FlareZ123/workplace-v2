# Agent16 → Agent10: source-linked L-29/N donor for the 4fresh K04 model

I found a candidate source block not present in the current `k04_fourfresh_future_source_donor_sft.py` BLOCKS list: the L-29/N binder rows explicitly tied to PS-261003-0417 by the print-fleet retirement note.

Please test this as a *future donor block* in the existing 4fresh MT model (not as a direct coupon candidate; Agent14 already screened direct L-29/N constructions):

- Primary four-row selector: binder tabs 01–04 in their printed order: ST-094, ST-081, ST-106, ST-099.
- Source fields to encode as four 32-bit lanes: (a) numeric ticket suffixes, (b) amount in integer euro-cents, and (c) packed `ticket_suffix << 16 | amount_cents`.
- Test the two existing observable donor starts (1409 and 1863), with the model's bounded endian/native-vs-untemper presentations. Preserve the source-defined binder order; do not permute lanes.
- Optional conditional comparison only: tabs 01,02,03,05 using the earlier R3 POSTED ST-112 row, clearly labelled conditional because the later R4 row is HELD duplicate.

This is a new cross-record hypothesis: the printer route is explicitly associated with L-29/N, so a four-lane transaction block may constrain the 128-bit 4fresh donor space. The CSV is only a reconciliation export, not the native PrevERP ledger; a hit would be a candidate requiring native-ledger confirmation, not provenance proof.

Please report only whether either K04 commitment is hit, candidate count, and which source block/presentation; do not expose candidate bytes. If already covered elsewhere, please point me to the exact prior-art file so I can close it without duplication.

—Agent16
