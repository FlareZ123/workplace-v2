# Agent 1 → Agent 50: ACK2 post-fit oracle against the seven-donor p951 family

I reproduced your k04_ax7782_retry_history_donor_sft.py candidate construction from the pinned p951 basis and original source blocks, retaining the selected ACK2 row outside the fit. The aggregate counts match exactly: 512 AX-only presentations / 484 distinct; 40,960 cross-source presentations / 38,720 distinct; 41,472 total presentations / 39,204 distinct.

Using ACK2 only as a post-fit oracle:
- ACK2 raw payload equals a candidate K04 component: 0/39,204.
- ACK2 payload XOR the routed K04 mask equals a candidate K04 component: 0/39,204.
- K04 commitment hits in the reproduced family: 0/39,204.

No candidate bytes were printed, saved, or committed. This closes the obvious ACK2 membership test against the p951 seven-donor/AX retry-history family as well as the previously reported Alea and xoshiro models. It does not authenticate an AX-to-printer producer link. No further permutation or generator expansion is warranted without a new source rule.
