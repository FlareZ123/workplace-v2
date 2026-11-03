# K04: preserved retry event used as a whole-packet source control

Agent 7, 3 November 2026. This is an exploratory historical-record reconstruction test, with no recovered component.

The selected `PS-261003-0417` RECOVER ACK attempt 2 has two earlier same-job buffers. An independent later job, `PS-261003-0420`, also has a RECOVER ACK attempt 2 and an earlier STORES ACK. The [reproducer](../agents/agent7/k04_retry_prior_buffer_kdf_sft.py) defines one fixed family of 24,300 hash-derived complete packet predictions using an earlier same-job buffer, preserved header fields, several standard digest functions, and fixed input layouts. The later job's entire ACK2 packet was held out.

* Later event holdout: 0 of 24,300 predictions match its complete 16-byte buffer.
* Selected event from earlier LABEL ACK: 0 of 24,300 predictions pass the original K04 component commitment.
* Selected event from earlier RECOVER REQUESTED: 0 of 24,300 predictions pass the original K04 component commitment.

All 48,600 selected-event candidates use the original immutable route mask and acceptance digest. No selected copied payload bytes are used in predicting them. Local original-source pilot completed the counts, including a planted whole-packet positive; the linked portable test has not separately run in CI. The original spool is pinned by SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

This excludes only the stated prior-buffer-derived candidate class and one later full-packet copied-source control. Neither record authenticates physical coupon bytes. The archive remains six verified components, with K04 and K08 unresolved.
