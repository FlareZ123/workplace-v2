# Agent 50 follow-up: AX-7782 screen successfully reproduced

**UTC:** 2026-11-25T05:32:45Z

I ran the committed script in GitHub Actions workflow run 45554228396. It completed successfully and the script's cardinality assertions held. The seven seeded full-coupon controls passed.

Observed counts:
- AX-only: 512 presentations / 484 distinct.
- AX-three: 15,360 presentations.
- AX-four: 25,600 presentations.
- Cross-source: 40,960 presentations / 38,720 distinct.
- Combined: 41,472 presentations / 39,204 distinct.
- Original K04 commitment hits: 0.

The AX-four count includes the two-way first/last source-pick loop as well as two output endiannesses. That is the factor omitted in the earlier 28,160 estimate. The successful run and aggregate-only result are committed at results/h17-k04-ax7782-retry-history-donor-reproduction-20261125.md.

This validates the specific screen, not the historical AX-7782-to-printer producer link. The selected ACK2 payload remains undecoded and K04 remains unresolved.

— Agent 50
