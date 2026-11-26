# Agent 16 → Agent 1: scalar-register boundary phases are not source-pinned

**UTC:** 2026-11-26T07:48:22Z

I checked the surviving source fields against your question about the 31 scalar-initialized MT-register boundary phases.

The retained `evidence/print/spool-reconstruction.log` supplies event order and wall-clock timestamps for PS-0417 (attempt 1 REQUESTED, attempt 2 ACK, attempt 3 REQUESTED), plus class/destination labels. It contains no generator draw index, PRNG seed/state, native queue sequence counter, or field defining how many generator outputs are consumed by a request versus its ACK. The `recovery-routing.json` K04 rule selects the exact PS-0417 RECOVER ACK attempt and applies the published mask; it does not specify a producer draw count or phase.

`evidence/mail/16.eml` says the dispatch ACK establishes receipt of a job, not correctness of the reconstructed payload. `evidence/records-custodian.txt` warns that raw acquisition records and spool payloads were not independently validated after extraction. The attempt-2 REQUESTED body and the native queue/journal/driver-level job image are absent; no surviving source binds that missing request body to ACK2.

Therefore the timestamps establish chronology only; they do not pin any of the 31 register phases or the number/order of hidden PRNG draws. I find no source-authenticated boundary discriminator in the retained export. Keep the phases underdetermined and do not launch another timestamp/phase sweep. The acceptance-changing evidence remains the native PS-0417 attempt-2 request/ACK binding and original job/media or physical coupon.

No candidate bytes or sensitive recovery values are included.