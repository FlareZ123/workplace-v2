# K04: full 128-bit generator-state exclusion for copied-ACK2-tail / later-REQUESTED3 triad

**Agent 8 · 28 November 2026 · complete original-source conditional mathematical exclusion · K04 remains MISSING**

## The exact source hypothesis (not the original printer's proven implementation)

Under the explicit **xoroshiro128++ 1.0 (49,21,28)** generator with consecutive native 64-bit outputs and a **64-bit big-endian, AB word serializer for the later triad**, hypothesize that:

- The **last eight bytes of the disputed copied PS0417/18:02 ACK attempt2** retain the genuine generator's native **output 3**. The *other* copied eight bytes are **never fitted** or assumed intact.
- The **two intact retained words of PS0417/18:03 REQUESTED attempt3** are exactly the generator's next native **outputs 4 and 5**, with no unobserved native draws, reset or intervening byte-order change.
- For each source-compatible generator state at output3, the hypothesized original selected 16-byte physical coupon would be **the two preceding native outputs 2 and 3**, serialized big-endian/AB. Apply the unchanged original K04 route XOR mask, compute full 16-byte SHA256 and compare the full original K04 commitment **before** an optional earlier REQUESTED1 replay diagnostic. This is the candidate-production/acceptance gate.

The copied ACK2 buffer is explicitly unauthenticated; the later REQUESTED3 is a request record, not proof of media output or even PRNG emission. Consequently **even a complete no-state proof here says only that those two surviving payload fragments cannot belong to this one consecutive-output producer model**. It neither reveals a physical K04 coupon nor excludes hidden output gaps, reordered words, altered ACK2 bytes, other serializers, resets, or another printer producer. No evidence authenticates xoroshiro as the printer engine.

## Why the search covers the *entire* original 128-bit state space

For the fixed generator **first output y3**, any proposed 64-bit first state word `a` determines the other 64bit state word `b` uniquely:

```
y3 = (rotl64(a+b,17)+a) mod 2^64
b  = (rotr64(y3-a,17)-a) mod 2^64
```

Thus all possible initial *128bit* generator states compatible with observed `y3` are exactly represented by all **2^64 choices of `a`**, with `b` derived algebraically. The native Boolean/ANF SMT circuit additionally requires both subsequent **complete 64-bit outputs y4 and y5**. Every source-compatible SAT state, if any, is blocked by its entire first-word value; solver **UNSAT** closes a cube only after any complete full-state models have been checked against original K04 acceptance first. Terminal **UNKNOWN is never deemed UNSAT**.

A disjoint 12-bit partition of the first state word uses `P12=(0,1,2,3,22,23,24,25,45,46,47,48)`, exactly **4,096** exhaustive parent cubes. Every terminal UNKNOWN P12 is partitioned into exactly sixteen disjoint P16 cubes by adding first-word bits `(4,5,6,7)`. Every terminal UNKNOWN P16 is further partitioned into exactly sixteen disjoint P20 cubes by adding bits `(8,9,10,11)`. All cube labels and state membership are verified by the independent source-private audit. This partitions the **entire state space**, not a sampled set of arbitrary seeds.

## **Final original-source aggregate and independent exact audit**

All **4,096** P12 parents have completed original pinned-source original input runs and have original private terminal records, no unvisited parents. Each P12 terminal UNKNOWN has its full sixteen children recorded; every terminal UNKNOWN P16 has its full sixteen grandchildren recorded.

| Original source-private proof depth | Exact disjoint cubes actually resolved | Terminal UNSAT | Terminal UNKNOWN | Full compatible 128-bit states |
| --- | ---: | ---: | ---: | ---: |
| P12 top level | **4,096 / 4,096** | **2,576** | **1,520** | **0** |
| P16, every P12 UNKNOWN | **24,320 / 24,320** | **24,316** | **4** | **0** |
| P20, every P16 UNKNOWN | **64 / 64** | **64** | **0** | **0** |
| **Fully certified P12 parents (after exact child resolution)** | **4,096 / 4,096** | **all source-empty** | **0 open** | **0** |

Independent fail-closed original-source ledger re-opened all 4,096 local original P12 caches, all 24,320 relevant P16 descendants and all 64 P20 descendants, checked exact disjoint parent membership, original source SHA pins, every stored SAT model's original three-word replay and complete original SHA before holdout (none recovered), and counted missing/UNKNOWN correctly. It returned:

```text
P12_exactly_closed_source_empty=4096
P12_exactly_closed_with_states=0
P12_open_due_to_unknown_or_missing=0
P12_unvisited=0
P12_terminal_unsat=2576
P12_unknown=1520
P16_children_recorded=24320
P16_terminal_unsat=24316
P16_unknown=4
P16_missing=0
P16_unknown_refined_closed=4
P20_children_recorded=64
P20_terminal_unsat=64
P20_unknown=0
P20_missing=0
source_states_p12=0
source_states_p16=0
original_K04_hits=0
original_REQUESTED1_replays=0
```

This is a **complete whole-domain mathematical source-incompatibility exclusion for the exact copied-tail8-plus-later-two-word, no-gap, big/AB hypothesis**. It is NOT a complete exclusion of all possible K04 physical coupons or even all xoroshiro serializations, and is not a commitment hit. In this original instance zero source-compatible states existed, so **zero candidate components were produced by this triad model**; do not misleadingly count the 28,480 solver cubes as completed original K04 SHA comparisons. The exact no-state conclusion itself is the original result.

## Reproducers and guardrails

- [P12 native Boolean source-private complete triad inverter](../agents/agent8/k04_triad_p12_source_private.py); [Boolean original-state circuit](../agents/agent8/k04_pruned_native.py).
- [P16 sixteen-way refinement of unresolved parents](../agents/agent8/k04_triad_p16_unknown_refiner_private.py).
- [P20 sixteen-way refinement of unresolved P16 cubes](../agents/agent8/k04_triad_p20_unknown_refiner_private.py).
- [Independent fail-closed P12/P16/P20 original source and full SHA checker](../agents/agent8/k04_triad_exact_source_ledger_audit.py). Supports the original local and public-runner private-cache layouts; audit refuses historical source in public GitHub Actions.
- Original input sources verified against the committed SHA256 pins `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` (spool), `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5` (route), and `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f` (acceptance). Original and private state caches reside outside the GitHub repository with owner-only permissions; no values or candidate material in this report.

An independent source-free seeded test recovered **4/4** planted complete 128bit states under the P12 triad circuit, plus **4/4** exact P16-true-state positive fixtures (64/64 child cubes correctly terminal after state blocking) and **4/4** exact P20-true-state positive fixtures. Arithmetic forward/inverse generator-state roundtrip controls also passed. These establish reachable SAT states and branch partition correctness under the implementation, not historical source truth. All original P12/P16/P20 workers exited cleanly and the final independent original audit returned no open partition. No GitHub Actions was used for historical source.

## Interpretation, limitation and priority

With three observed independent-looking 64-bit outputs and only a 128bit unknown state, a generic mapping would already be overdetermined by 64 bits; failure to fit is **expected** absent a genuine shared producer. The exact negative is nevertheless useful: the *specific* historical triad hypothesis is now exhaustively closed without leaving 1,520 first-stage UNKNOWN cubes to be mistaken for possibilities. Another inference based on an intact copied ACK2 tail plus identical immediate later output pair should not be repeatedly relaunched with only SAT parameter changes. A new study must offer an independent archive-selected producer, stage, skip rule or actual selected native printer receipt.

Separately, a **different initial-state big/BA source-positive producer** was previously replayed on 1.28 billion original full K04 coupon assignments with zero hits; see [the disjoint original state complete-target report](h17-k04-second-bigba-state-bidirectional-1280m-fullcoupon-20261128.md). That state also fails complete independently retained ACK predictions under the explicit zero-skip source row history. The two experiments have distinct original source assumptions; do not merge their logical conclusions.

**Original official REC8/1 remains K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING, combined INCOMPLETE**. No original physical coupon or author-final margin was recovered; no source, candidate, verifier, route, acceptance or quarantined PDF was modified or accessed.
