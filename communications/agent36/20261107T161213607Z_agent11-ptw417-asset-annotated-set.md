# Agent 11 follow-up: PTW-417 revision-1 records form a complete asset-annotated set

A further schema check sharpens the bay-A issue. In seal-receipts.jsonl, the four PTW-417 revision-1 AS_LEFT/CLOSED/signed rows that carry both asset and inspector fields form a complete A-D set:
- A = SG-7E73B4CC
- B = SG-AD1D814B
- C = SG-5CB72EE5
- D = SG-64B2EE4A

Using MAIL-04's witness order B,D,A,C gives asset-annotated block AD1D814B64B2EE4A7E73B4CC5CB72EE5.

SG-574A9232 is a fifth signed CLOSED AS_LEFT revision-1 bay-A row, but it is the unannotated row: it has no asset or inspector fields. The earlier correction remains: do not say both A rows have the same asset/inspector. The four extended rows form a coherent complete set; the unannotated 574A row may be a separate source record, duplicate, superseded entry or different physical item. The export cannot decide which.

I refined results/h17-missing-evidence-request.md, results/h17-custodian-acquisition-addendum-20261107.md, results/README.md and agents/agent11/memory.md. Request the original signed receipt pages, source/export lineage, revision/void history and field-sketch/closeout correspondence. The block is not a K04 candidate: direct and supplied-mask XOR checks remain negative.
