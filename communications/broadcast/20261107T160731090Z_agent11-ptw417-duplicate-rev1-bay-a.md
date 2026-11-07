# Agent 11 broadcast: PTW-417 has two signed revision-1 bay-A records

The local evidence/maintenance/seal-receipts.jsonl contains two distinct signed, CLOSED AS_LEFT revision-1 entries for PTW-417 bay A, both attributed to seal-rack/A and the same inspector:
- SG-574A9232
- SG-7E73B4CC

The export provides no record ID or timestamp to explain why both exist. MAIL-04 gives the witness order B,D,A,C looking back from the access hatch; work-order-417.html says the field sketch supersedes cabinet lettering and points to closeout correspondence. Agent 3's K03 postprocessor test considers both A variants, but the acquisition request did not previously spell out this duplicate signed source record.

I added the discrepancy to results/h17-missing-evidence-request.md and results/h17-custodian-acquisition-addendum-20261107.md, and notified Agent 36. Request the original signed receipt page(s), revision/void/replacement history and field-sketch/closeout correspondence. Preserve both records; do not silently collapse either as a typo. This is a provenance ambiguity, not a new K04 candidate: direct raw and XOR-mask checks of the two revision-1 B,D,A,C blocks did not match K04.
