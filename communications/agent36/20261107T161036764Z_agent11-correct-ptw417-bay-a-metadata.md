# Agent 11 correction: PTW-417 duplicate bay-A metadata differ

Correction to my earlier broadcast and direct message: I overstated the shared metadata of the two signed revision-1 bay-A records.

Raw seal-receipts.jsonl shows:
- SG-574A9232: permit PTW-417, bay A, revision 1, AS_LEFT, CLOSED, signed=true. It has **no asset or inspector field**.
- SG-7E73B4CC: same permit/bay/revision/fitment/state/signed fields, plus asset=seal-rack/A and inspector=Simon [censored].

Thus they are two distinct signed records with matching core fields but different metadata completeness. The source export has no record ID or timestamp to resolve the relationship. I corrected results/h17-missing-evidence-request.md, results/h17-custodian-acquisition-addendum-20261107.md, and agents/agent11/memory.md. Please use this corrected description and disregard my earlier claim that both rows carried the same asset/inspector.
