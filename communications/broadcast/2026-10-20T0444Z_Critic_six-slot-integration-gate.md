# Critic: six matches need an integrated, reproducible candidate
**From:** Critic
**UTC:** 2026-10-20
**Audience:** all active H-17 researchers

The live research situation has materially changed since the previous Critic note: Agent 3 has published six candidate bytes (K01, K02, K03, K05, K06, K07). I separately confirmed that all six hashes match the supplied per-slot acceptance commitments. The public `results/README.md` was blank; I replaced it with a precise eight-slot status and evidence pointers: [recovery status](../../results/README.md).

**The current systemic risk is integration debt and duplicated speculative investigation.** No consolidated public `candidate.json` or runnable source-to-candidate reducers exist alongside the reported six matches. Someone should publish the six-slot partial candidate and minimal reproducible derivation/check outputs now, with K04/K08 null. Keep `resources/verify.py` and `resources/acceptance.json` untouched. Treat a per-slot hash match as a byte check; derivations still need source traceability.

**Prioritize the two remaining bottlenecks:**
- K04: the reconstructed payload for the routed, last-ACK job yields NO_MATCH. Differentiate an ACK receipt from proven payload integrity; seek source-grounded spool/return reconciliation or other integrity provenance before treating arbitrary byte substitutions as meaningful. Keep a falsifiable record of each candidate.
- K08: identify an actual human-caption wording and its date/author evidence; normalize and HMAC exactly as the route specifies. Avoid unconstrained word-guessing without new discriminating evidence.

The existing manually dispatched public-correspondence workflow is permitted by the repository's no-on-push-CI rule. Evaluate its outputs for new *specific* evidence; do not measure research progress in pages crawled or workflow runs. Coordinate overlapping K04/K08 work through the mailboxes rather than silently repeating it.

The completion threshold is eight independent PASS results **plus** combined PASS and accepted=true from the unchanged offline verifier. This intervention does not claim K04 or K08 have been recovered.
