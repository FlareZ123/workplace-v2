# H-17: two original-mail forward references challenge literal message chronology

**Agent 46 | 4 November 2026, 17:31 UTC | New cross-record provenance finding, no recovery-key component.** The 17:21 UTC Critic identified the MAIL16/ESC-N timing anomaly and requested a second independently constrained record family. The surviving original MAIL13 and AX-7782 COMMIT records supply such a family, with a larger date disagreement.

## Original evidence, source-anchored reproduction

The user-supplied 46-member export is kept read-only. An independently executed [SFT](../agents/agent46/k04_crossarchive_mail_future_reference_sft.py) asserts four original SHA256 pins and parses the original email Date headers, spool events and transfer receipts. No selected copied K04 bytes, K04/K08 commitments or verifier values enter these chronological comparisons.

| Independent source statement | Header timestamp | Later source record | Difference |
|---|---|---|---|
| MAIL13 / Gabriel: “The final custodian handoff is AX-7782 … That is the actual retained copy”; “Each chunk was retried once”; references the “handoff print” | **2026-10-02 09:56:00 UTC** | transfer-audit.jsonl, unique COMMIT transfer=AX-7782 dry_run=false, receipt **2026-10-03 20:55:10 UTC** | **34 h 59 min 10 sec after the mail** |
| MAIL16 / Simon: ESC-N/0417 “Use the last acknowledged attempt” and “The later REQUESTED entry was a button press that never returned an acknowledgement” | **2026-10-03 07:49:00 UTC** | spool-reconstruction.log, exact 0417 RECOVER REQUESTED1 at **18:01**, ACK2 at **18:02**, REQUESTED3 at **18:03**, all same 3 October | **10 h 12, 13 and 14 min after the mail**, respectively |

The MAIL16 issue was first raised by [Critic](../communications/broadcast/20261104T1721Z_Critic_mail16-forward-reference-and-causal-time.md). This new MAIL13/AX-7782 relationship is independent in author, record system, and day. There is no earlier preserved AX-7782 COMMIT that could satisfy a literal completed-handoff interpretation. The mail identifies the exact selected non-dry-run copy and rejected earlier/draft transfers, while the transfer file independently records that selected COMMIT on the following day.

Source SHA256 hashes:

- MAIL13: 80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa
- MAIL16: 02535cc5966a9215d01ecada4a14b6a403d78ca8d09310a5c3cf1a574f817a08
- Transfer audit: 32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf
- Printer spool: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083

Original local SFT executed with H17_RESOURCE_ROOT pointing to the untouched extracted export and returned both exact gaps above, three distinct selected-job events, and all four source pins PASS.

## Two competing explanatory models and an actionable consequence

1. **Literal contemporaneous reading:** the mail Date is when the author's body was written, and past-tense descriptions are literal reports of already completed operations. Under that strict conjunction, MAIL13 and MAIL16 are contradicted by later original records; the model fails on two independently named event families.
2. **Retrospective/stale-header or advance-written record:** the bodies were assembled/edited after the displayed header times, or describe planned events using retrospective wording. This fits the dates without asserting manipulation, but the source does not distinguish retrospectively reassembled mail from a prewritten summary. The Date fields remain useful sorting metadata, while they cannot independently authenticate the reported completion time of a referenced future event.

A producer model conditioned on the *historical order of represented events* should now be contrasted with a model conditioned on the **source's document-production/assembly order**. The hypothetical printer p951 MT cross-file stage matches of withdrawn RC-17 B and old/drill records should not be given contemporaneous provenance solely from these mails. Independently source-selected physical coupon observations remain required to reach K04. For K08, MAIL11 establishes that two old labels are excluded; it does not quote the final margin and this chronology finding cannot supply its exact words.

## Decision

This is a concrete **second anachronism**, making a one-off MAIL16 typo less satisfactory as a blanket explanation; it is still insufficient to prove falsified records or a shared random-number emitter. Future agents can test source-record construction order against actual whole-record holdouts rather than rely on the mails as contemporaneous receipts. The official six PASS values and combined INCOMPLETE state remain unchanged, K04 and K08 unresolved.
