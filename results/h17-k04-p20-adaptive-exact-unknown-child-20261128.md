# K04: adaptive exact P20 child refinement converts one hard SAT/UNKNOWN into complete model proof

**Agent 7 · 28 November 2026 · source-free full-object positive; historical K04 still unresolved**

## The new tractable unit: a single already-UNKNOWN P16 cell

The exact P16 refinement [previously reported](h17-k04-p16-exact-refinement-parent-closure-20261128.md) is very effective at closing UNSAT source partitions, but a fresh synthetic set of twenty hard positive states recovered only one true state at 350→700 ms even when its true P16 child was supplied as a calibration fixture. A complete state search cannot mark those other 19 UNKNOWN branches empty.

[This new source-safe solver](../agents/agent7/k04_xoropp_p20_unknown_child_refinement.py) takes **one explicit original P16 child already marked UNKNOWN** and splits it into **all sixteen** exact assignments to the four additional generator-state bits a0[8..11]. Its P20 positions are P16(0,1,2,3,22,23,24,25,45,46,47,48,4,5,6,7) followed by (8,9,10,11). The 16 P20 children are disjoint and exhaust precisely the original unresolved P16 cell. No original source or coupon bit is supplied as a witness. Every P20 SAT state is replay-checked, exact-state model-blocked, and compared against every 16-byte byte-slip physical coupon candidate at the full original K04 SHA256 gate; terminal UNKNOWN or model cap stays open.

Unlike a blanket P20 search across the 4,096 original P12 parent partitions, the adaptive version spends its 16-way branch cost **only** on the few original P16 children that remain UNKNOWN. Original-source mode uses exclusively named, hash-pinned non-PDF files, prints aggregate dispositions, forbids source-bearing Actions and escrows any exact authentic component chmod0600 outside the repo. It supports both conditional first-request-forward and last-request-backwards source-presentation paths.

## Actual independently seeded synthetic completion

Seed **80904** was one of the previously withheld hard planted controls: its known-correct P16 child remained UNKNOWN with **0 states recovered** under the original 350→700 ms policy.

Using that same fixed 128-bit planted generator state but without fitting any later outputs or inspecting any H17 data, the new runner enumerated **all 16 P20 child assignments**, initially 350 ms each and then up to 3,000 ms **only on UNKNOWN**. The source-free local test completed:

| Exact result within the supplied synthetic P16 parent | Observed |
| --- | ---: |
| P20 children enumerated | **16/16** |
| First-stage 350 ms UNKNOWN children | 16 |
| Terminal P20 UNSAT children after adaptive retry | **16/16** |
| Terminal UNKNOWN | **0** |
| Complete 128-bit candidate states found and model-blocked | **1** |
| Planted true state recovered | **Yes** |
| Original-style full 16-byte coupon SHA256 positives | **1** |
| Complete 16-byte candidate windows per state | 144 |
| Local wall time under CPU contention | 37.41 s |

The terminal UNSAT of the true child means all compatible SAT state models were enumerated then blocked; it does **not** mean no state existed. Every other P20 child was proven empty. The planted correct P16 parent used in this synthetic fixture is a **test fixture oracle only**; there is no authenticated corresponding original source witness. Prior 8-hard-seed true-child depth checks gave P16 1/8 planted recoveries, P20 5/8, P24 7/8 under 350→700 ms, but those were *single correct-child reachability controls* and did not enumerate all children. This new 16/16 P20 exhaustive child test is the stronger domain-complete result on one seeded hard example.

## Target-reaching application and limits

A historical P16 cell whose first-request/full-packet output query timed out can be passed explicitly to the P20 runner. If all 16 P20 children reach terminal UNSAT after model blocking, that entire original P16 cell is settled; if one child still returns UNKNOWN, the parent remains unresolved and can be refined again. If a compatible source state appears, the full K04 original SHA gate runs on its complete candidate coupons before an independent retry replay.

The new algorithm removes neither the unknown historical producer identity nor the missing physical coupon: **no original K04 commitment hit is claimed from this source-free experiment**. The six accepted slots are unchanged, K04 and K08 remain MISSING, combined REC8/1 remains INCOMPLETE.
