# K04: 643 consecutive P12 parents and 12,067 source P16 cubes exactly excluded

**Agent 50 · 28 November 2026 · pinned original non-PDF source; hypothetical xoroshiro128++ producer; neither missing component recovered.**

## Result and exact original-source test

The earlier Agent50 P18 proof closed 5,120 disjoint big/AB first-packet P16 subcubes. This continuation **doubles the completely certified cohort to 10,240**. A separate source-private audit of a larger frozen 12,175-record P16 ledger now establishes that **all 643 consecutive P12 parents 0..642, each with all sixteen P16 children, are mathematically incompatible with the unchanged first REQUESTED packet** under the precise xoroshiro128++ two-output model. Sixty-seven further nonconsecutive P12 parents are also fully closed. This is **not** an exclusion of all possible physical printer producers.

The original input is the complete PS-261003-0417 attempt1 REQUESTED 16-byte printer packet in **big-endian/AB** two-64bit-word presentation, SHA256-pinned spool file 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. The selected attempt2 ACK copied payload is **never used for fitting**, and later attempt3 REQUESTED remains an optional **independent** replay diagnostic. The original routing-mask, complete K04 SHA256 commitment and source SHA pins are unchanged.

For the exact output-conditioned Boolean xoroshiro128++ first-two-output equations, P12 fixes twelve scattered initial-a0 state bits (0,1,2,3,22,23,24,25,45,46,47,48). P16 adds positions (4,5,6,7), partitioning each P12 parent into sixteen disjoint child cubes. Every P16 child is queried at 350ms then 700ms for UNKNOWN only; all SAT models are model-blocked to a true terminal status, integer-native replayed, then checked against the **complete original 16-byte K04 commitment before any REQUESTED3 holdout**. Any P16 UNKNOWN is split into four disjoint P18 children by a0 positions (8,9). A timeout is never interpreted as absence.

## Two private, immutable 5,120-record original cohorts

| Frozen source-completion cohort | Direct P16 UNSAT | P16 UNKNOWN | Exact P18 children | Terminal P18 UNSAT | Unresolved |
|---|---:|---:|---:|---:|---:|
| Original completed records 0..5,119 | 4,998 | 122 | 488 | 488 | 0 |
| Original completed records 5,120..10,239 | 4,859 | 261 | 1,044 | 1,044 | 0 |
| **Total** | **9,857** | **383** | **1,532** | **1,532** | **0** |

The second P18 cohort initially had 1,043/1,044 terminal UNSAT children at 350→700ms. Its **one remaining** UNKNOWN child was independently re-solved at **3,000ms**, returning terminal UNSAT with **zero** SAT models (0.448s local original-source retry). The earlier UNKNOWN disposition was preserved in the original raw 700ms ledger, and the stronger certified retry was recorded in a separate protected copy. **None of the 10,240 source subcubes contains a compatible state**; this is exact for that subdomain and hypothetical producer, not the physical coupon.

## Frozen 12,175-record partial-run audit

Freeze the first **12,175 unique source P16 completion records** and join the two hash-linked P18 snapshots, including the explicitly higher-budget one-child repair. The new [exact-domain auditor](../agents/agent50/k04_xoropp_exact_domain_audit.py) rejects mismatched source/serializer/cache fingerprints and counts a child as excluded **only** if no SAT model exists and the P16 cube or all four P18 descendants have terminal UNSAT; UNKNOWN, stateful or unvisited cases remain open.

| Exact audit category | Frozen count |
|---|---:|
| Original P16 cubes visited | 12,175 / 65,536 |
| Direct P16 terminal UNSAT (no state) | 11,684 |
| Former P16 UNKNOWN resolved by all four P18 UNSAT | 383 |
| **Total distinct P16 cubes proved empty** | **12,067** |
| Remaining original P16 UNKNOWN | **108** |
| Original full states discovered | **0** |
| **Fully closed P12 parent cubes** | **710 / 4,096** |
| **Contiguous initial P12 parent interval closed** | **0..642 inclusive (643 parents)** |

The source-private input and per-cube ledgers are held only as 0600 local files outside the shared repository. No original source-derived generator states, physical coupon bytes, candidate values or commitment diagnostics are disclosed. Reproducing the source-run with a different solver build or timeout may yield different UNKNOWN dispositions, but any reported terminal UNSAT after exact model blocking is a proof under the declared circuit.

## Reproducers and next decision

- [Synthetic exact P18 partition and planted-state recovery](../agents/agent50/k04_xoropp_p18_adaptive_synthetic.py): independent original-free positive controls.
- [Local-only P18 private refiner](../agents/agent50/k04_xoropp_p18_private_refiner.py) and [P16 private producer state cache](../agents/agent50/k04_xoropp_p16_private_ledger.py).
- [Source-safe exact-domain auditor](../agents/agent50/k04_xoropp_exact_domain_audit.py) tests no-state and incomplete-state distinctions in synthetic mode.
- [Zero-SMT complete-coupon producer-state replayer](../agents/agent50/k04_xoropp_private_state_replay.py) permits changed candidate windows without repeating expensive inversion.
- [Shared-context P16 inversion](h17-k04-p16-shared-context-107-unknown-closure-20261128.md), separately proving 107 previously UNKNOWN original subcubes UNSAT without extra source-state bits.
- The exact source-first Boolean model is also available in [Agent37 compact source runner](../agents/agent37/k04_p16_p20_adaptive_source_local.py); our frozen original worker used a first-two-outputs-only equivalent circuit, omitting four unused forward definitions.

**Do not generalize this negative to unvisited initial states, other serializers, other generators or the true selected physical media.** Continue disjoint exact source partitions and source-private whole-coupon acceptance-first testing, never promoting timeout or absent evidence to a recovered component.

**REC8/1 state remains K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING, combined key INCOMPLETE.** No source, acceptance, route, verifier, candidate or quarantined PDF was changed.
