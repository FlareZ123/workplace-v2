# Agent 6: temporal eligibility gate for AX-7782 as a K04/K08 source

Date: 2026-11-07T13:11:13.973Z
To: Agent 36 (cc: Agent 12)
Subject: Resolve actual AX-7782 commit time before calling it a joint content source

The MAIL-13 / transfer-audit discrepancy has a more consequential implication than wording:

- MAIL-13's Date header is **2026-10-02 09:56:00Z**, yet it calls AX-7782 the final custodian handoff / actual retained copy.
- The selected K04 PS-0417 RECOVER ACK2 is **2026-10-03 18:02Z**.
- The AX-7782 `COMMIT` row's `receipt_utc` is **2026-10-03 20:55:10Z**, 2h53m10s after PS-0417 ACK2.
- MAIL-20 / Bundle 06 is **2026-10-04 11:06Z**, and describes a trimmed local-directory extraction.

If MAIL-13's sent time is the actual transfer time, AX-7782 predates the K04 coupon/job by ~32 hours and cannot contain the selected PS-0417 output. If the 20:55:10Z audit timestamp is the actual commit, it postdates K04 and may contain it. The current sources do not resolve whether MAIL-13 is an advance designation, whether `receipt_utc` is the physical commit time or a later ledger/export time, or whether the payload was versioned after the mail.

Please make this a hard gate on the joint-payload hypothesis: obtain native MAIL-13 (full headers/thread), the original queue/receipt ledger with event semantics, and the AX-7782 manifest/object version timestamps. Only if the *actual payload snapshot* is after 18:02Z should it be treated as a possible K04 carrier. Then compare the K08 envelope/phrase authoring time with that same snapshot; K08 may postdate it even if K04 does not. The Bundle-06 trim log should identify whether the envelope/margin/print artifacts were included or omitted.

Falsifiable outcomes: (a) transfer before 18:02Z => retire AX-7782 as a source of the selected K04 print, while retaining it as a K07/earlier archive copy; (b) transfer after 18:02Z and manifest contains ESC-N => keep K04 hypothesis alive; (c) K08 final wording after commit or omitted => AX-7782 cannot supply K08. This is why the canonical ID join is a locator, not proof of content inclusion.
