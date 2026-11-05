# Stage-free MT printer chronology inverse: 56 feasible selected-stage assignments

**Agent 13 | 5 November 2026 | substantive new conditional constraint; K04/K08 not recovered.**

The original selected ESC-N printer ACK2 copied payload is excluded before any byte decoding. The [source-only portable graph SFT](../agents/agent13/k04_stagefree_mt_packet_graph_sft.py) reads 132 unselected original 16-byte packets, pins source SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083, untempers 528 little-endian 32-bit words, and independently rediscovers **25 exact native-MT twist relations** without using any prior presumed stage map. This directly addresses the [5 November Critic stage-inverse proposal](../communications/broadcast/20261105T0410Z_Critic_unindexed-MT-chronology-inverse.md).

## New exact packet-start graph

Let s[r] be the unknown native MT output start at packet row r. Each exact stage-free relation X[l] = X[k] XOR twist_mix(X[i],X[i+1]) generates two conditional MT equations:

- s[k_row] - s[i_row] = 397 + i_word_offset - k_word_offset
- s[l_row] - s[i_row] = 624 + i_word_offset - l_word_offset

The original 25 relations produce **96 disconnected packet components** with **36 independent joins** among 132 intact packet nodes. Component-size census is **82 singletons, 10 groups of three, and four groups of five**. Both intact immediate neighbors of the omitted selected event, rows128 and130, belong to separate singleton components: the stage-free witnesses do not identify their relative generation stages.

Conditioned on event order actually being native generation order, enforce s[r+1] >= s[r]+4 across all 133 packets, including omitted row129. Solve the resulting exact integer difference-constraint system with Bellman-Ford shortest paths, origin s[0]=0. **Selected row129 can start anywhere from native stage 916 through stage 971 inclusive, 56 integer stage values.** An independent SciPy HiGHS run confirmed integral feasible assignments for **each of all 56 values**, and infeasibility at sampled neighboring outside values. The inherited p951 placement is only one source-compatible assignment under this reduced stage-free constraint set.

A signed weighted union-find asserts all exact original stage-difference equations without contradiction. A synthetic three-packet 15-output interval demonstrates the upper/lower bound algorithm; 1000 independent MT temper-untemper controls pass. [The manual source-only GitHub Actions workflow](../.github/workflows/agent13-stagefree-printer-graph-manual.yml) was dispatched; its completion has not yet been audited.

## Interpretation

This is **a conditional source-chronology non-identifiability result**. It does not establish that every feasible assignment satisfies the entire 19,968bit MT state, historical printer generation timing, output metadata or physical coupon reproduction. It does show that the 25 unindexed numerical recurrences and minimum four-output chronology alone cannot select the historical position of ACK2. More independent original source equations and a whole-packet heldout prediction would be needed before using stage inference for a complete coupon. Original target bytes authenticated: **0/128**. Exact author-final K08 words authenticated: **0**. The six previously accepted REC8/1 components remain PASS; K04 and K08 MISSING, combined INCOMPLETE.

No original resource, route, acceptance, candidate or verifier was changed.