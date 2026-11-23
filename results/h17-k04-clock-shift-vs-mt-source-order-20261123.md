# K04: an eleven-hour spool-clock correction conflicts with the observed MT word order

**Agent 21 | 23 November 2026 | Original-source temporal discriminator; no coupon recovered**

## Question and stakes

MAIL-16 at **03 Oct 2026 07:49 UTC** refers to a later PS-0417 attempt-3 REQUESTED entry that the original spool explicitly timestamps **18:03:00Z**. Interpreting the five terminal `Z` records as local wall time erroneously labeled UTC and subtracting **11 hours** would put attempt3 at 07:03 UTC, before the email. This conditional chronology has been proposed independently; it may motivate inserting the selected K04 attempt2 at the beginning of the printer generator's observable stream. Before that change can inform a source-to-coupon constructor, test its prediction against the exact existing native-word relationships.

The question here is narrower than whether the printer clock was wrong: **can a UTC+11 relabeling coexist with the 42 exact MT recurrence witnesses and a single printer writer that emits packets in chronological order?**

## Method

Read the unchanged **132 intact original** spool packets and omit the disputed selected row129 ACK2 payload *before decoding*. Pin the original `spool-reconstruction.log` SHA256 as `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Untemper the four native 32-bit little-endian words in each intact packet. Independently re-extract all triplets satisfying the native MT19937 recurrence `X[t+624] = X[t+397] XOR twist(X[t], X[t+1])`, including the established firstword/top-bit partial witness convention. The extractor reproduces the previous **25 complete and 17 partial** original witnesses. An independent planted full-recurrence word positive passes.

Five original-source witness triplets involve terminal rows. Rows are zero-indexed in source order:

| Earlier word-bearing row | Midstream word-bearing row | Later word-bearing row | MT relationship |
| --- | --- | --- | --- |
| 43 | 96 | 128 | Firstword partial |
| 44 | 97 | 130 | Firstword partial |
| 44 | 97 | 131 | Complete |
| 45 | 98 | 132 | Firstword partial |
| 45 | 98 | 132 | Complete |

For each witness, standard native MT stage differences force `stage(later) > stage(midstream)`. If the writer emits packets in stage order and their timestamps describe generation time, **the late cohort's corrected UTC time must remain after the corresponding midstream time**. Subtracting 11 hours violates all five relationships.

The tightest constraint is row130 at 18:03 versus row97 at 15:05. It permits a common clock correction **strictly less than 2 hours 58 minutes**. The change needed to make the 18:03 attempt3 precede MAIL-16 at 07:49 is **at least 10 hours 14 minutes**. These two bounds have no overlap.

## Finding and limits

This falsifies the *combined* hypothesis of (a) a common positive clock correction large enough to reconcile MAIL-16, (b) a single MT19937 producer behind the exact retained word relationships, and (c) chronological packet generation corresponding to the spool records. It is a sharper restriction than noting that the original timestamps carry an explicit `Z` suffix.

It **does not prove** the clock was synchronized, that MT19937 was the real printer firmware, or that source/export ordering equals emission ordering. A buffered or asynchronous print pipeline, multiple issuers, a mistaken mail date, or an unrelated reason for the mathematical MT witnesses could break the combined assumptions. Existing source caution about incomplete/damaged payload extraction remains in force. Both complete MT word witnesses are valuable because they constrain the late cohort without decoding row129's copied bytes, but they do not authenticate a particular physical coupon.

**Decision:** Do not relocate selected PS-0417 attempt2 to 07:02 UTC *and* retain a monotone common-MT model as a source-supported way of resolving its 128 bits. A future model making the selected coupon accessible via a different event/copy-stage sequence must first explain the old-to-late complete-word links without chronological contradictions. The original published selector remains PS-0417 RECOVER last ACK attempt2. No original K04 whole coupon was emitted, and the original K04 SHA256 was **NOT_EVALUATED** in this source-only test. K08 remains missing; combined REC8/1 remains incomplete.

## Reproducer

[One-file, read-only exact-original spool SFT](../agents/agent21/k04_late_clock_mt_witness_sft.py) accepts either the repository `resources` directory (default) or the supplied original ZIP, pins source bytes, checks all 42 original word witnesses, verifies the five cross-cohort links, runs a synthetic fullword positive, and asserts the contradictory **178-minute / 614-minute** bounds. Local execution against the supplied original archive returned PASS, five cross-links and `UTC_plus_11_monotone_shared_MT_compatible=false`. No source, canonical candidate, acceptance or verifier was modified.

Cross-reference: [the original UTC+11 proposal](../communications/broadcast/20261123T074154Z_agent1-k04-local-clock-event-boundary.md), [all-42 MT original-source derivation](h17-k04-fourfresh-direct-antecedent-obstruction-20261123.md), and [live decision map](README.md).
