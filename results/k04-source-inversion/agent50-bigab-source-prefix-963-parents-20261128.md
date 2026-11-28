# K04 source-domain closure: 963 consecutive P12 parents

**Agent 50 · 28 November 2026 · pinned original non-PDF spool; hypothetical xoroshiro128++ first-packet big/AB; no accepted K04 or K08.**

## Exact original computation

The 16-byte retained PS-261003-0417 ATTEMPT=1 STATE=REQUESTED original packet is modeled as two consecutive big-endian/AB 64-bit xoroshiro128++ outputs. Selected ATTEMPT=2 ACK copied material is entirely **withheld**. The exact first-two-output Boolean equation partitions all unknown initial-state word a0 values into 4096 P12 parents fixing bits (0,1,2,3,22,23,24,25,45,46,47,48), then sixteen P16 children each by bits (4,5,6,7). Every SAT full state is model-blocked and integer-native replayed; complete unchanged K04 commitment tests precede optional independent later REQUESTED3 replays. No original initial state-bit witness is assumed.

Each P16 terminal UNKNOWN is split exhaustively by additional a0 bits (8,9) into **four disjoint P18 grandchildren**. Only terminal UNSAT with no states in *all four* grandchildren closes an UNKNOWN parent. The first two source-private cohorts (5,120 P16 each) were documented in the [prior exact report](../h17-k04-bigab-643-parent-10240-p16-exact-closure-20261128.md).

**New third original-source cohort, unique P16 records 10,240..15,359 in worker-completion order:** 4,772 direct terminal UNSAT; 348 initially UNKNOWN; all **1,392** exact P18 grandchildren terminal UNSAT, zero P18 unknown and zero full generator states. Thirty children initially UNKNOWN at 350→700ms received independent 3,000-ms exact retries which all returned UNSAT. The original timeout dispositions are retained privately. P18 source-local wall time 509 seconds.

| Immutable source cohort | Direct P16 UNSAT | P16 initial UNKNOWN | Final P18 grandchildren UNSAT | P16 still open | State models |
| --- | ---: | ---: | ---: | ---: | ---: |
| First 5,120 | 4,998 | 122 | 488 | 0 | 0 |
| Second 5,120 | 4,859 | 261 | 1,044 | 0 | 0 |
| Third 5,120 | **4,772** | **348** | **1,392** | **0** | **0** |
| **Complete first three cohorts** | **14,629** | **731** | **2,924** | **0** | **0** |

## Strict 17,920-source-record frozen audit

A separate frozen snapshot contains exactly the first **17,920 unique** P16 source records. The fourth 2,560-record cohort is currently only partially proved: 2,256 direct UNSAT and **304 still UNKNOWN**. The [read-only exact coverage auditor](../../agents/agent50/k04_xoropp_exact_domain_audit.py) validates all three original P18 ledgers against SHA-linked frozen inputs and refuses to count any UNKNOWN, stateful or unvisited cube as excluded.

| Exact original big/AB source status | Frozen count |
| --- | ---: |
| Distinct P16 source cubes visited | **17,920 / 65,536** |
| Direct P16 terminal UNSAT with zero compatible state | **16,885** |
| Previously UNKNOWN P16 resolved by all-four P18 UNSAT | **731** |
| **Distinct P16 cubes proved empty** | **17,616 / 65,536** |
| Remaining source-visited P16 UNKNOWN | **304** |
| Source-compatible initial generator states | **0** |
| Fully proved-empty P12 parents | **1,020 / 4,096** |
| **Consecutive proved-empty P12 prefix** | **0..962 inclusive (963 parents)** |

Every one of the sixteen P16 children in each P12 parent 0..962 is included in the exact empty-state proof; 57 additional complete P12 parents lie outside the prefix. These claims are **not** derived from the source ledger record order, which is worker-unordered. A prior 643-parent original-source checkpoint is strictly subsumed. The source-private ledgers remain in local mode0600 files, not in GitHub or public CI.

## Reusable route to completing the source search

Committed source-free [compact two-output solver](../../agents/agent50/k04_xoropp_compact_firstpair_solver.py), [P18 exact split and planted-state controls](../../agents/agent50/k04_xoropp_p18_adaptive_synthetic.py), [original-safe 3-second P18 escalation](../../agents/agent50/k04_xoropp_p18_private_refiner.py), [resumable source-private state cache](../../agents/agent50/k04_xoropp_p16_private_ledger.py), [zero-SMT complete-coupon replayer](../../agents/agent50/k04_xoropp_private_state_replay.py) and [strict source-domain audit](../../agents/agent50/k04_xoropp_exact_domain_audit.py) preserve all found candidate states and proof statuses. Synthetic controls recover exact planted states, including both distinct states with identical first-packet outputs. The original spool SHA256 is pinned to 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.

**Boundary:** This exact exclusion is conditional on one hypothetical PRNG, one serializer and one original source interpretation; it neither authenticates the historical printer nor reveals selected physical K04 coupon bits. Other serializers, producer families and the unresolved P16 cubes remain open. K01/K02/K03/K05/K06/K07 individually PASS, K04/K08 MISSING, combined REC8/1 INCOMPLETE. No original resource, acceptance, verifier, canonical candidate or restricted PDF was changed or inspected.
