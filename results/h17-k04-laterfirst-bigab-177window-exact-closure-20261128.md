# K04 later-first big/AB exact 177-window source search — new 140-parent closure

**Agent 6 · 28 November 2026 · confidential local original-source aggregate + source-free controls; no recovered K04.**

## Causal question and scope

Can the selected physical K04 coupon have come from an xoroshiro128++ 1.0 output stream that remained continuous to the intact **later** PS-261003-0417 REQUESTED attempt-3 packet, even if the earlier REQUESTED attempt-1 was reset, copied, or unrelated? This is the independently established *later-first* hypothesis ([Agent1's method](h17-k04-xoropp-laterfirst-backwards-coupon-recovery-20261128.md)), not an assertion that the printer actually used the generator.

The model deliberately fits **only the later intact REQUESTED3 16-byte pair** under big-endian 64-bit serialization and word order AB. The selected, physically unverified ACK attempt-2 copied payload is **not** read or fitted. The earlier first attempt is not used as an acceptance veto.

A 128-bit internal state is conditioned on the later two 64-bit outputs using the source-independent, one-transition exact Boolean circuit developed by Agent15. The first 64-bit state's sparse P12 anchor enumerates all 4096 possible partitions; each selected parent is decomposed exactly into sixteen P16 children using extra bits 4..7. Only a still-UNKNOWN child is recursively decomposed into sixteen P20 descendants using bits 8..11, then four P22 descendants using bits 12..13 when necessary. **All** compatible states in a region must be explicitly model-blocked to terminal solver UNSAT before that region is called closed; timeouts and model caps remain UNKNOWN.

For each SAT state, invert the exact xoroshiro transition 24 steps, serialize the 24 prior 64-bit outputs in chronological big-endian order, and test **all 177 contiguous full 16-byte windows** in the resulting 192-byte prehistory. This expands the earlier 18 aligned two-output windows to include every one of 15 possible intermediate byte offsets at each relevant boundary, without fitting any copied ACK byte. Every predicted complete coupon is XOR-reduced by the unchanged K04 route mask and compared against the unchanged original **full SHA-256** K04 commitment. Only an original commitment hit could yield a private component; intermediate states or source compatibility alone are not acceptance.

## Predeclared independent controls

The public source-free fixture tested 10,000 random exact forward/inverse state-transition round trips and six independent synthetic planted states. Each planted complete 128-bit state was recovered from its two output words in its planted P16, P20 and P22 partition (18/18 direct full-state reachability checks). Six synthetic planted full 16-byte coupon commitments were detected at random offsets within the 177-window prehistory. These are **algorithm controls only**, not historical printer evidence or K04 recovery.

The original-source input is limited to the SHA-256 pinned non-PDF spool (digest `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`), original routing mask and acceptance commitment. Any accepted component would be retained in a chmod-0600 out-of-repository private escrow. No original state, packet bytes, target hash or candidate coupon is printed, committed or uploaded to public CI. BX25-08 and derivatives are not opened.

## Original-source exact result, P12 parent partitions 116..255 inclusive

Two disjoint local batches ran with four workers, 350 ms per exact solver query, fully model-blocked, adaptive partition depth up to P22.

| Parent range | Parents exhaustively closed | P16 checks / terminal UNSAT | P20 checks / terminal UNSAT | P22 checks | SAT states | Complete original K04 checks | Original hits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 116..131 | 16/16 | 256 / 253 | 48 / 48 | 0 | 0 | 0 | 0 |
| 132..255 | 124/124 | 1,984 / 1,874 | 1,760 / 1,760 | 0 | 0 | 0 | 0 |
| **Union** | **140/140** | **2,240 / 2,127** | **1,808 / 1,808** | **0** | **0** | **0** | **0** |

Thus these **140 exact P12 partitions** are source-empty under the declared generator/serializer hypothesis. There is no inferred historical state in this range, so zero K04 comparisons is not a set of generated coupons that failed acceptance. No conclusion follows about P12 partitions outside these bounds, other serializers, actual physical coupon stage, alternative PRNGs, or whether this producer existed historically. This result closes a previously unresolved 140-parent *later-first big/AB* domain without overclaiming K04 recovery.

## Decisional next experiment

Continue disjoint later-first big/AB original-source P12 parents **256..1023**, then **1024..4095**, using the same exact partition and every full-window acceptance reducer on any SAT state. Do not rerun the already-closed 116..255 region. Separate historical parent sets 0..115 were partially explored by other identities, and 9 of those UNKNOWNs were closed independently by Agent15; eventual full coverage must account for their remaining UNKNOWN branches. An original K04 commitment hit would be a candidate, while authenticity additionally requires printer-causality evidence.

The standalone local executable that produced this confidential aggregate result has the same state and 177-window construction as [Agent6's source-safe modular reproducer](../agents/agent6/k04_laterfirst_bigab_177_exact_source_local.py). It is restricted to private/local original-source execution; no public CI original run is authorized. This is a **conditional mathematical exclusion and reusable complete-coupon mechanism**, not an accepted seventh component.

**Acceptance remains:** K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined REC8/1 INCOMPLETE.
