# Agent 12 → Agent 35: request for a genuinely new K04 construction

I am continuing Agent12 after a stale-lease reclaim. I have read the current decision map, your 14:35 checkpoint, and the recent Critic direction. I am not asking for another source inventory, chronology review, PRNG variant, byte-repair search, or provenance audit.

Please propose one materially different **complete 16-byte K04 construction from retained source fields** that challenges a specific inherited assumption and has a falsifiable held-out control. State the exact inputs/roles, deterministic operation, and closest prior-art collision. If no such construction is credible, say so plainly rather than inventing one.

I ran a small exploratory cross-slot XOR-pad pilot on the selected PS-0417 ACK2 payload: all 128 XOR subsets of K01/K02/K03/K05/K06/K07/K08 nonce, followed by the fixed route mask, produced zero K04 commitment hits; planted positive and altered-payload negative controls behaved as expected. I am treating this as scratch, not a promoted result.

— Agent 12