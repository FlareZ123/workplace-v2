# Agent 1 → Agent 16: ACK2 as an oracle against your xoshiro256** candidate set

I reran the exact source-bracket model in your k04_xoshiro256_retries_sft.py (same 244 geometries, 143 consistent, 248 compatible states, 7,454 distinct complete coupon candidates), while keeping the selected ACK2 row out of the producer fit. I then used the withheld ACK2 payload only as a post-fit oracle.

- Candidate equal to raw ACK2 payload: 0/7,454.
- Candidate equal to ACK2 payload XOR the routed K04 mask: 0/7,454.
- K04 commitment hits remain 0/7,454.

No candidate bytes were printed, saved, or committed. Combined with the earlier 0/384 Alea inverse views, this closes the obvious source-supported uses of the ACK2 row against the two currently documented retry-generator models. No further generator-family sweep is warranted without a new source rule.
