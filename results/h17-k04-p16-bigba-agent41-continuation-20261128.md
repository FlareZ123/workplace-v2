# K04 P16 big/BA continuation: parents 592..999 exactly closed

**Agent 41 · 28 November 2026 · local original-source aggregate result; no K04 recovery**

## Result

I continued Agent7's exact P16 refinement on the same hash-pinned PS-0417 `REQUESTED1` first packet, conditional xoroshiro128++ producer model and declared **64-bit big-endian / BA packet-word serializer**. The predecessor report had reached parent 591. This continuation starts at parent **592** and stops before parent **1000**, so it does not repeat that historical range.

The P12 parent is refined by all 16 assignments to state bits `[4,5,6,7]`. Every P16 child is an exact disjoint subcube. Each child fits only the intact first two output words; a solver `UNKNOWN` is unresolved and is never treated as exclusion. A recovered complete state would be reduced through all 144 preselected-packet/byte-slip windows (9 hidden-packet gaps × 16 byte offsets), with the unchanged K04 commitment checked before any later-packet diagnostic.

Final aggregate for **P12 parents 592..999 inclusive**:

| Metric | Result |
| --- | ---: |
| New P12 parents | **408** |
| Exact P16 child subcubes | **6,528** |
| Terminal UNSAT children | **6,528** |
| Terminal UNKNOWN children | **0** |
| Complete first-packet states found | **0** |
| Original K04 commitment hits | **0** |

An initial resource-contended parallel pass left 100 child checks `UNKNOWN` across parents 836..847. Those twelve parents were not counted closed. I then reran all 192 P16 children in those parents as isolated exact solver processes under the same 350 ms first check and 700 ms UNKNOWN retry. All **192/192** terminated `UNSAT`, including all 100 previously unresolved children. No state/coupon value was needed to obtain that closure.

## Reproducibility and boundary

The local runner pins the surviving non-PDF spool, route and acceptance files to the repository hashes used by the existing P16 work. Historical source processing stayed local; the quarantined BX25-08 PDF and derivatives were not read. Public output contains only method and aggregate disposition. No source payload, inferred state, candidate coupon or target diagnostic is published.

This result is a **conditional producer/view exclusion**, not printer authentication and not an accepted K04 component. It materially extends the exact big/BA P16 search frontier by 408 consecutive P12 parents. Parents outside this interval and unresolved partitions in earlier/later work remain separate; no conclusion is drawn about other serializers or producer hypotheses.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain unresolved; REC8/1 remains incomplete.
