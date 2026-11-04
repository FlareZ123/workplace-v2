# H-17 mail-header/event-time dependence: two original forward references (4 November 2026)

**Agent 3.** Original-source, read-only chronology investigation. This expands the Critic's 17:21 UTC MAIL16 observation with an independent earlier MAIL13/AX-transfer reference. It does **not** recover K04 or K08, identify the historical source-generation algorithm, or invalidate the untouched REC8 verifier.

## Two source-matched prepublication gaps

| Original source | Header/body claim | Separately retained event | Forward difference |
| --- | --- | --- | --- |
| `mail/13.eml`, Fri 2 Oct **09:56 UTC** | Gabriel says final custodian handoff **AX-7782**, describes **AX-7783** as already stopped before handoff and AX-7781 as dry-run | `transfers/transfer-audit.jsonl` has AX-7782 COMMIT, `dry_run=false`, and AX-7783 ABORT, **both receipt_utc = 3 Oct 20:55:10 UTC** | **34 h 59 min 10 s** |
| `mail/16.eml`, Sat 3 Oct **07:49 UTC** | Simon says, for selected ESC-N, the **later REQUESTED entry** had no acknowledgement | The exact ESC-N job PS-261003-0417 has ATTEMPT 1 REQUESTED 18:01, ATTEMPT 2 ACK 18:02, ATTEMPT 3 REQUESTED **18:03 UTC**, with no later ACK | **10 h 14 min** |

These are *record-specific referent matches*, rather than vague anticipation of a future date. In MAIL13 the completed outcome of AX-7783 is named 34 h 59 min before the separately timestamped abort. In MAIL16 the only REQUESTED attempt later than the selected final ACK is attempt 3, ten hours after the email header. Both source timestamp types explicitly denote UTC. The transfer file assigns the same receipt timestamp to all four transfer outcomes, consistent with batch ledger recording but without authenticating the physical event time.

**Source SHA256 anchors**: MAIL13 `80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa`; MAIL16 `02535cc5966a9215d01ecada4a14b6a403d78ca8d09310a5c3cf1a574f817a08`; spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; transfer ledger `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`; routes `146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad`.

## Causal models and discriminators

1. **Literal contemporaneous mail headers and literal event times** require another pre-mail AX-7782/7783 completed handoff and another ESC-N REQUESTED-after-ACK event. The **supplied records contain neither**. The model could still survive through historical records outside this trimmed export, email-header errors, or a different intended referent; the export alone does not make these possibilities logically impossible.
2. **Retrospective body, stale header, or export-time reconstruction** predicts future outcome references appearing under old headers. Both original comparisons match that pattern. Records custodian says *mail ordering* was retained by UTC date; that statement does not independently authenticate original body creation times. This explanation is plausible, **not proven**.
3. **Staged event chronology or batch-stamped ledger** predicts event timestamps may not be exact real-world completion times. All four transfer receipts sharing `2026-10-03T20:55:10Z` is a concrete reason to investigate this alternative; it does not explain the printer 18:03 ACK-versus-REQUESTED reference by itself.

The 1 Oct MAIL11 authorization of RC-17 C agrees with the 30 Sep revision register and is a control showing not every email has an obvious future-event mismatch. The 3 Oct 21:47 MAIL18 incident-preservation notice is later than the 20:55 AX receipts and 21:14 telemetry window, also time-compatible under the displayed timestamps.

## Operational implication for cracking K04 / K08

MAIL16's account of the selected attempt and MAIL13's selection of the transfer **must not be double-counted as independent contemporary witnesses** for stage-coupled generator hypotheses. They can still be reliable **instructions for the reducer**: K07 AX-7782 and K04 ESC-N 0417 ACK attempt2 remain the documented selections, and the original six-slot verification is unaffected. Their authoring dates are unproved.

The new investigative target is the **document-generation/transmission boundary**: identify a preserved earlier version, original issuer/dispatch record, or source-side transformation that explains how an apparent later outcome was inserted into an older email. A stage-selecting candidate should predict a complete intact same-role packet or a verbatim caption before predicting K04/K08. This is a chronology-dependent model-discriminator, not a license to regard the missing cryptographic values as found.

Reproducer: [source-only SFT](../agents/agent3/h17_timing_prepublication_sft.py). No official source, route, candidate, verifier, or acceptance commitment modified.
