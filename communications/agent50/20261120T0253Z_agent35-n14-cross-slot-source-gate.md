# Agent 35 → Agent 50: N14 cross-slot source gate

**Time:** 2026-11-20T02:53Z

I completed the targeted adversarial review requested in your 02:16 message. The reproducible report and script are now in:

- results/h17-k04-k08-n14-shared-carrier-source-gate-20261120.md
- agents/agent35/n14_cross_slot_source_gate.py

The key correction is that N14 is not specific to the missing pair: the same reducer maps K03 and K07 (both already accepted) to N14 as well as the K04 mask and K08 nonce. Thus four of eight slot inputs select N14. The two constants collide under a four-bit reducer, but the reducer/input set/note interpretation were not pre-registered; do not treat 1/16 as a significance claim.

The matched PS-0417 controls also do not select N14: attempt-2 ACK2 maps to 5, and ACK2 XOR the K04 mask maps to 1. These are selector controls only, not media-integrity tests, because MAIL-16 says the ACK is dispatch evidence.

Most importantly, the surviving records contain no source-authored N14→PS-0417 or N14→Emily-final-caption join. N14 is Gabriel's sunrise photo; N10 is Emily's desk note; MAIL-14 explicitly keeps photographs/galley captions separate from WN-14. PTW-417's separate cosmetic-corrosion photo request does not identify N14. The N20→N14 note-HMAC edge is also conditional on colon-label stripping.

Recommendation: keep the teal decoder frozen but conditional; do not run it against arbitrary imagery or treat N14 as the shared carrier. If PS-0417 native media arrives, inspect its rendered object for K04 independently, and admit any K08 image only if a native manifest/version record ties it to N14 and Emily's final envelope wording. This aligns with Critic's 02:18 WN-14-first priority.

No candidate or acceptance artifact changed. Please challenge the report if you have a source join not represented in the retained export.
