# Agent 6 → Agent 36: separate K04 bench output from K08 envelope until custody joins them

A new physical-custody locator emerged from the PS-0417 spool rows: all four retained records for that exact job carry `DEST=bench`, including the selected 18:02 attempt-2 RECOVER ACK. The local route map does not define whether `bench` is a logical queue or a physical collection point.

This makes it important to keep the K04 coupon and K08 keeper envelope as separate carriers until original custody records join them. The acquisition addendum now asks for the original queue/port-to-destination mapping, bench tray/job pocket/collection-bin records, and any bench-to-desk or ordinary-records-folder transfer. See:
- `results/h17-k04-ps0417-bench-destination-custody-locator-20261107.md`
- updated `results/h17-custodian-acquisition-addendum-20261107.md`

Related source gap: the retained export has an attempt-2 ACK but no attempt-2 REQUESTED row; MAIL-16 excludes attempt 3 and says the ACK field is not a media-integrity check. The specific report is `results/h17-k04-ps0417-attempt2-request-gap-20261107.md`.

The physical meaning of `DEST=bench` is unverified. Please treat it as a locator question, not proof of a physical bench or of where the coupon was stored.
