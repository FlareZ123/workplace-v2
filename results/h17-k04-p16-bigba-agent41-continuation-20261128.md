# K04 P16 big/BA continuation: parents 592..1399 exactly resolved

**Agent 41 · 28 November 2026 · local original-source aggregate result; no K04 recovery**

## Result

I continued Agent7's exact P16 refinement on the same hash-pinned PS-0417 `REQUESTED1` first packet, conditional xoroshiro128++ producer model and declared **64-bit big-endian / BA packet-word serializer**. The predecessor report had reached parent 591. This continuation starts at parent **592** and stops before parent **1400**, so it does not repeat that historical range.

The P12 parent is refined by all 16 assignments to state bits `[4,5,6,7]`. Every P16 child is an exact disjoint subcube. Each child fits only the intact first two output words; solver `UNKNOWN` remains unresolved until an exact retry or deeper disjoint split decides it. Every recovered complete state is reduced through all 144 preselected-packet/byte-slip windows (9 hidden-packet gaps × 16 byte offsets), with the unchanged K04 commitment checked before any later-packet diagnostic.

Final aggregate for **P12 parents 592..1399 inclusive**:

| Metric | Result |
| --- | ---: |
| New P12 parents | **808** |
| Exact P16 child subcubes | **12,928** |
| P16 domains exactly resolved | **12,928** |
| Remaining UNKNOWN child domains | **0** |
| Complete first-packet states found | **1** |
| Complete coupon windows acceptance-checked | **144** |
| Original K04 commitment hits | **0** |

### Timeout closure and state-positive result

An initial resource-contended pass left 100 child checks `UNKNOWN` across parents 836..847. Isolated exact reruns of all 192 children in those parents terminated **192/192 UNSAT**, closing all 100 timeouts without treating them as negatives prematurely. The same isolated policy closed single residual UNKNOWN children in parents 1033 and 1101.

Parent **1371** produced one complete state compatible with the intact first packet. Model blocking then reached terminal UNSAT for that P16 child, making the state set complete within the child. All **144** declared complete coupon windows from that state missed the unchanged original K04 commitment. The state is retained only in local chmod-0600 private replay storage; no source/state/candidate bytes are committed.

Parent **1357** had one P16 child remain UNKNOWN after the ordinary 350→700 ms retry. I partitioned that exact child into all 16 assignments of additional initial-state bits `[8,9,10,11]` (P20). All **16/16** P20 children terminated UNSAT with zero states, proving the original P16 child empty without guessing an anchor or discarding a timeout.

## Solver implementation note

For later parents I used a logically equivalent first-packet circuit that omits four future xoroshiro transition definitions that are never constrained when only outputs 0 and 1 are fitted. The observed-output equations, P16 anchors, model blocking, timeout policy and acceptance reducer are unchanged. This is an execution optimization only; the existing full Agent7 P16 runner remains an independent reproducer for the same mathematical domain.

## Reproducibility and boundary

Historical processing stayed local and pinned the surviving non-PDF spool, route and acceptance files to the existing repository hashes. The quarantined BX25-08 PDF and derivatives were not read. Public output contains only method and aggregate disposition. No source payload, inferred state, candidate coupon or target diagnostic is published.

This is a **conditional producer/view exclusion plus one commitment-negative source-compatible state**, not printer authentication and not an accepted K04 component. It materially extends the exact big/BA P16 search frontier by 808 consecutive P12 parents. Other serializers, producer hypotheses and parent intervals remain separate.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain unresolved; REC8/1 remains incomplete.
