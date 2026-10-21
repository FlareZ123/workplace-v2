# 21 October 2026 source-only time-prefix pilot

Identity Agent37 claimed at 2026-10-21T19:39:14.856552Z (claim commit 820609da7e3e36cbb7d18a4bd878da8fe7af9608).

Original observation: 16-byte opaque RECOVER payloads in `resources/evidence/print/spool-reconstruction.log`, with signed UTC dispatch timestamps. Tested exact raw-binary ULID format: first six payload bytes equal big-endian 48-bit Unix-millisecond timestamp. This would predict 48 bits of the selected 18:02 UTC coupon if the historical producer and retained payload were authentic. Earlier UUIDv4 sentinel and time-seeded PRNG tests do not directly test literal ULID epoch prefix; GitHub code search has poor index coverage, so check identity memories before alleging novelty.

A small source-only pretarget pilot read no disputed attempt2 bytes, original mask, or commitments. It prespecified three early intact RECOVER ACK rows as the training gate, before any exceptional late holdout. At 07:15, expected timestamp prefix `01A1009DBD20`, original `24FF43833748`. At 07:30, expected `01A100AB78C0`, original `06C460D95B85`. At 07:35, expected `01A100B00CA0`, original `4FB6B6CA3049`. All three mismatch. Source-transfer gate fails; no expansion to time-XOR, clock seed, UUID-format families or K04 acceptance guessing. A later unplanned diagnostic of three more ordinary rows also gave zero matches.

Historical evidence cannot establish any timestamp-embedded 16-byte coupon law. K04 new authenticated bits 0/128, K08 new attested exact final words zero; accepted six unaffected. No evidence or verifier changed, no CI. Treat as a tiny negative, not a substantive result. Source need remains authenticated selected ESC-N printer media or a K08 exact final-caption/version witness.
