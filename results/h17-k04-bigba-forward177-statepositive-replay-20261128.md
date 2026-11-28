# K04: actual big/BA state-positive replay over 33 new full-coupon byte offsets

**Agent 8 · 28 November 2026 ~11:46 UTC · original source/private model and SHA acceptance checked · K04 still MISSING**

## Actual discriminating result

A 28 November Critic broadcast identified **two** authentic-source-packet-compatible initial xoroshiro128++ states produced by Agents 7 and 41 under the **intact earlier PS-261003-0417 REQUESTED1, big-endian/BA** conditional generator/view. Those agents had evaluated **144** full-coupon windows per model and reported no K04 commitment hit. Increasing source-empty parent counts without replaying these already-known states misses an inexpensive opportunity.

Agent8 independently reconstructed Agent41's source-compatible state from **P12 parent 1371** (not the private model bytes from Agent41, which were never accessed). All **16/16 disjoint P16 children** were explored with source-pinned original REQUESTED1 as the only fitted output:
- **15/16 child state domains terminal no-state UNSAT**;
- **1/16 child domain terminal UNSAT after enumerating exactly one complete source-compatible initial state**;
- **0 UNKNOWN**. Thus the parent is **fully enumerated with a compatible state**, not source-empty.

From the complete compatible state, advance exactly two generator outputs beyond the known intact REQUESTED1 packet, generate 24 **later** complete generator words, serialize 12 full 16-byte packets under big-endian/BA, and evaluate **all 177 possible contiguous complete 16-byte byte windows** in the resulting 192-byte stream. Apply the original route mask, full original K04 SHA256, and escrow any actual passing 16-byte component privately, **before** any optional later REQUESTED3 holdout. Never fit a copied/disputed ACK2 payload.

Agent7's original 144-window reducer used 9 hidden gap values 0..8 with all 16 slips, starting at absolute serialized-stream offsets **16..159** *including* the known REQUESTED1 packet. After explicitly removing that first packet, the same 144 starts are relative offsets **0..143**, and the 177-window continuation adds **33 newly tested complete-coupon starts at relative offsets 144..176** (absolute 160..192). This correct relative-byte mapping was cross-checked against Agent7's source code for the original 144-window reducer; no source bytes or state model values appear here.

| Field | Original-source result |
| --- | ---: |
| First-packet-compatible complete states captured in parent1371 | **1** |
| Baseline original 144 complete SHA checks (relative offsets 0..143) | 144 |
| **Additional whole-coupon checks at relative offsets 144..176** | **33** |
| Total whole-coupon checks against unchanged original K04 commitment | **177** |
| Accepted original component hits, baseline | 0 |
| Accepted original component hits, added offsets | **0** |
| Terminal unresolved P16 children | 0 |

This **closes the extra 33-byte-start reducer on one real source-compatible model**, rather than adding another empty-parent sweep. It does **not** authenticate xoroshiro128++ as the historical printer generator, prove there was a 10th hidden packet, or recover the selected physical coupon. Agent7's distinct firstpacket state elsewhere in parents16..591 remains for its private owner to replay; this result does not claim that second state was checked.

## Reproducibility and positive controls

[Source-safe private producer and 177-offset target reducer](../agents/agent8/k04_bigba_forward177_replay.py) is committed. Its source-free deterministic mode covers **8 new initial states × 9 strategically selected offsets = 72 complete full-SHA positives** including old/new boundary positions 143/144 and final offset176. It cross-validates the forward next-24-word sequence against an independent one-step stream and packet serializer. The original-source script pins the original spool/routing/acceptance SHA, forbids public CI, requires an existing private owner-only cache, and prints only counts; the complete state and any passing coupon are persisted mode0600 outside GitHub. Local actual original run took **6.86 seconds** for exact parent1371 state re-enumeration and 177 checks; a cached rerun recomputed all177 SHA checks without re-solving, preserving the same zero-hit result.

**Decision:** Original K04 still MISSING; no acceptance-changing files altered. This finite additional byte-stage hypothesis has been tested against one true source-compatible state and failed; before further expensive inversion, the other owner should cheaply replay their previously discovered state against these 33 offset starts if that state still exists privately. More speculative phases need a source-visible reason and synthetic whole-component control. K08 remains missing, six other slots PASS and combined REC8/1 INCOMPLETE.