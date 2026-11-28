# H-17 K04: reverse-first little/BA complete-coupon byte-slip search

**Agent 8 · 28 November 2026 · source-free positive mechanism plus bounded original-source trial; no seventh recovered component**

## New objective-relevant route

The forward-first K04 producer hypothesis fits the intact REQUESTED1 packet and predicts the lost selected ACK2. A distinct plausible retry-stage relation is that the lost selected ACK2 and intact REQUESTED3 shared a generator state even if REQUESTED1 was separately seeded. **Prior work:** Agent1 implemented mathematical reverse recovery; Agent7 independently implemented a **144-position reverse-first full-byte-slip coupon reducer** in [`h17-k04-laterfirst-p16-byte-slip-20261128.md`](h17-k04-laterfirst-p16-byte-slip-20261128.md); Agent13 owns the actual **big/AB** later-first source lane. This work is a **different little-endian/BA original-source stage**, extends that prior reverse reducer to **177 positions**, and adds a private per-state P12 fast-first ledger. No original ACK2 payload is used to fit the state.

1. Parse the single unchanged PS-261003-0417 ATTEMPT=3 STATE=REQUESTED CLASS=RECOVER record as the first two complete 64-bit outputs under little/BA.
2. Partition the unknown first state into source-independent **P12** cubes, or refine to 16 disjoint **P16** child cubes by additional bits 4..7, then enumerate every actual SAT model with complete-state blocking. UNSAT with no models excludes only that child; an UNKNOWN remains unresolved.
3. For each recovered complete xoroshiro128++ 1.0 state, apply the **exact inverse transition** 24 times to reconstruct 24 complete historical earlier generator words. Serialize 12 whole packets in little/BA.
4. Independently evaluate the **177 complete 16-byte contiguous byte-slip windows** of the 192-byte preceding stream. XOR each window with the unchanged original route mask, check the unchanged **full SHA256 original K04 commitment first**, and, if accepted, escrow the actual recovered 16-byte K04 component in an outside-repository mode0600 file. A possible REQUESTED1 replay is an *optional diagnostic*, never a target veto.
5. The private ledger preserves a source/circuit/serializer-stamped complete-state set and exact terminal UNKNOWN/UNSAT for every attempted P12 or P16 cube. An interrupted scan can distinguish completed, unresolved and unvisited cubes without publishing any derived original payload or candidate.

Compared with Agent1's 18 word-aligned offsets and Agent7's later-first **144 continuous byte-slip offsets (33..176)**, this reducer tests **all 177 offsets (0..176)** inside the 24 hypothesized preceding words. Thus the genuinely additional byte-start domain is **33 earlier offsets (0..32)**, not a newly discovered copy-stage. The 480 planted positives include **192** offset-controls outside Agent7's 144-position domain (6 early offsets × 32 state/layout fixtures); the other 288 reproduce the previously covered domain independently. The larger bound is an exploratory hypothesis, not a source-attested copy-stage.

## Source-free positive calibration

[Native-carry first-packet solver](../agents/agent8/k04_pruned_native.py) and [reverse-first source-safe runner](../agents/agent8/k04_reverse_littleba_private.py) are committed. The deterministic synthetic run \`python agents/agent8/k04_reverse_littleba_private.py --synthetic\` did **not** read any H-17 source, nonce, route, target, PDF, selected ACK2 or accepted components.

- 32 independent seeded generator-state/layout fixtures: 8 distinct seeded states per each of 4 byte-order/word-order serializers.
- 24 reverse transitions replay the exact original forward state and independently serialized stream in all fixtures.
- Fifteen planted complete-coupon offsets per fixture across the preceding 192-byte stream: **480/480 original-style full SHA256 coupon hits**, uniquely recovered at their planted byte positions.
- Separate planted *solver + reducer* integration on 8 freshly seeded correct-P12-cube fixtures, 3000ms/check-SAT with model blocking: **2/8 complete initial states and exact full commitments recovered**; six true-cube searches returned UNKNOWN without states. All eight terminal statuses were UNKNOWN after potential model-blocking, so none is a uniqueness or full-domain certificate. This emphasizes why synthetic reducer coverage cannot be mistaken for solver liveness.

## Original-source conditional results at first checkpoint

The original intact PS-0417 REQUESTED3 packet, the route mask and the original commitment were read only in a local nonpublic runtime; each file's original SHA256 is pinned in the script. The encrypted hash-only supplementary PDF was not opened, listed or examined.

On disjoint **P12 parents 0..15**, P16 child refinement at 350ms + 700ms retry examined exactly 256 16-bit state partitions in four local workers:

| Exact terminal disposition | Count |
| --- | ---: |
| P16 children fully UNSAT with zero state | **99** |
| P16 children unresolved UNKNOWN after retry | **157** |
| P16 children with enumerated SAT models | **0** |
| Complete P12 parents closed | **0/16** |
| Original K04 full-commitment hits | **0** |

This is a conditional state-space reduction, **not** a source-model exclusion and not an original K04 no-hit denominator over all states: UNKNOWN still contains potential state witnesses.

A separate P12 candidate-first original-source scan with a 3000ms per-call budget initially visited four disjoint 50-parent intervals (0..49, 1024..1073, 2048..2097, 3072..3121): **200 visited, 200 UNKNOWN, zero enumerated states and zero original K04 hits**. It uses a secure local per-parent ledger and will not assert that an UNKNOWN parent contains no matching state. This broad screen tests candidate latency, not the complete negative domain. Later completed coverage must be reported separately; no attempt-2 guessed or copied ACK bytes are fitted.


## Exact P16 coordinate refinement: source reachability and held-out recovery

Agent7's original geometry adds initial-state bit positions (4,5,6,7) to the 12 fixed anchor bits. Agent8 screened five alternative exact four-bit subpartitions on later-first little/BA source parents 0–3, then extended three candidate geometries to the next 12 parents. Each geometry is an exhaustive disjoint subdivision of its P12 parent. All original-source evaluations kept ACK2 withheld, checked any complete 16-byte coupon against the unchanged K04 SHA first, and printed no derived source values. Counts below are subcubes **proven empty UNSAT**, not hypotheses about absent historical states.

| Additional anchor bits | First 64 original children UNSAT | Next 192 original children UNSAT | Total UNSAT | Open UNKNOWN |
| --- | ---: | ---: | ---: | ---: |
| 4,5,6,7 (prior Agent7 geometry) | 50 | 149 | **199/256** | 57 |
| 26,27,28,29 | 55 | 103 | **158/256** | 98 |
| 49,50,51,52 | 30 | 99 | **129/256** | 127 |
| 8,9,10,11 | 1 | not run | 1/64 | 63 |
| 13,14,15,16 | 0 | not run | 0/64 | 64 |
| 60,61,62,63 | 4 | not run | 4/64 | 60 |

**All examined original children returned zero complete SAT models and zero K04 commitment hits.** Unknown children remain open. The first 64 source children misleadingly favored 26..29; the next 192 reversed that ranking. No selector was chosen as a new source fact.

**Source-free planted state controls:** First, an exploratory 32-seed comparison (Python Random seeds 20017–20048, the genuine 16 anchor bits supplied) recovered exact initial states in 17/32 for 4..7, 21/32 for 26..29, 20/32 for 49..52 and 16/32 for 60..63. Second, an independent 128-seed comparison (seeds 50000–50127) gave **119/128 exact complete-state recoveries for 4..7** and **109/128 for 26..29** under the same 350→700ms per-solve caps. All true-bit anchored controls avoided a false terminal UNSAT with no recovered state. Source-free reproducer: [128-seed comparison](../agents/agent8/k04_p16_coordinate_heldout.py). These are **conditional true-anchor tests**, not source-free recovery of the correct historical anchor.

The original P16 (4..7) first-16-parent screen had earlier recorded only 99/256 UNSAT on a more heavily CPU-oversubscribed four-worker run. The separately timed, less contended comparison above proved 199/256 UNSAT at nominally the same caps. This is a timeout effect, not contradictory mathematical proofs: UNSAT is conclusive for its exact subcube; UNKNOWN is not. Coordinate rankings at short solver budgets are scheduling-dependent and must be validated on realistic workloads.

The [confidential later-first runner](../agents/agent8/k04_reverse_littleba_private.py) now accepts independently configured four additional P16 bits, source/circuit/geometry-fingerprinted mode0600 state ledgers, an explicit UNKNOWN-only P12 retry preserving the union of previously discovered states, and a source-free-of-bytes **private coverage report**. Coverage distinguishes 4,096 expected P12 parents or 65,536 P16 children, visited, terminal UNSAT with/without models, open UNKNOWN, unvisited, and securely cached states; no source-derived state is printed. One original P16 parent16 integrated source test at 26..29 recorded **7/16 terminal UNSAT, 9/16 UNKNOWN, zero states and zero original K04 hits** in its replayable private ledger. Neither the added 33 earlier byte-slip positions nor the new geometry is attested printer behavior.



## 28 November ~11:34 UTC — first 16 parent groups exactly source-empty via P20/P22

The original firstpacket-only P12 candidate-first screen of the intact later REQUESTED3 little/BA view yielded almost no decisive models: at termination **2,555 of 4,096 disjoint P12 parents visited, 16 no-state UNSAT, 2,539 UNKNOWN and 1,541 unvisited**, with **zero enumerated complete states and zero K04 target hits**. A timeout is not a source exclusion. The scan was deliberately stopped rather than spending the remaining lease on statistically large but mathematically uninformative UNKNOWN coverage; all 2,555 per-parent dispositions were privately retained.

We instead refined the genuinely unresolved earlier **P16 parent interval [0,16)** (99 fully empty P16 subcubes, 157 UNKNOWN), using exact disjoint additional a0 initial-state bit positions 8..11. For each of 157 open P16 children, **all sixteen** P20 descendants were solved, each with 350ms first / 700ms UNKNOWN retry and complete actual-state enumeration, before the full 177-window original K04 commitment. Exactly **2,511/2,512 P20 grandchildren** terminated UNSAT with zero states. The one P20 UNKNOWN was itself subdivided into **four** exact P22 grandchildren at state positions12,13; all four terminated UNSAT with zero states. The P20/P22 method follows Agent4's independently developed adaptive reverse-first state-domain design; this is a **different tested original-source packet serializer**, not a claim that Agent8 discovered the P20/P22 technique.

**Thus all 16 consecutive P12 parents [0,16) are mathematically source-empty under this later-first little/BA xoroshiro128++ view.** Exact full-domain closure, not a count of attempted solver calls:

| Exact disjoint layer | Entire source-conditioned range | Fully empty terminal UNSAT | Unresolved after all descendants |
| --- | ---: | ---: | ---: |
| P16 subcubes | 256, of which 157 entered refinement | 99 | 0 |
| P20 subcubes below the 157 P16 UNKNOWNs | 2,512 | 2,511 | 0 |
| P22 subcubes below the single P20 UNKNOWN | 4 | 4 | 0 |
| P12 parents with fully exhausted descendants and zero compatible states | **16** | **16** | **0** |

No compatible state, reconstructed physical coupon or original K04 full-commitment match appeared in this covered interval. An original printer source outside the specified generator, byte/word layout, or claimed stage is not excluded. Remaining P12 parents **16..4095** are unresolved/unvisited by this *exact* deep proof; the broad P12-first-sat timeouts do not change that.

**Controls:** 16/16 seeded source-free true-P20-cube exact complete state and planted 177-window full SHA positives; 8/8 fresh true-P22-cube complete-state controls. Independently run [private exact-domain auditor](../agents/agent8/k04_reverse_proof_audit.py) produced **16 source-empty, zero model-bearing, zero unresolved parents**, 99 P16 UNSAT, 157 P16 UNKNOWN refined, 2,511 P20 UNSAT, one P20 UNKNOWN refined, four P22 UNSAT; missing-subcubes count 0 and no original target hit escrow. It checks full original source/circuit/model/view/geometry fingerprints on all private per-child files, emits no source-derived state values, and treats missing or UNKNOWN descendants as open, never UNSAT. Original-source code:
[exact P20 rescuer](../agents/agent8/k04_reverse_p20_private.py) and [P22/P24/P26 recursive rescuer](../agents/agent8/k04_reverse_deep_private.py), both strictly private-source local with synthetic positive controls, plus the existing P16 source and secure cache.

**Next substantive action underway:** four disjoint 16-parent original-source lanes [16,32), [32,48), [48,64), [64,80) run this entire P16→P20→P22 cascade on the same unchanged intact REQUESTED3 little/BA and original K04 commitment. Their final parent-complete receipts, not timeout-heavy first-SAT sweeps, should determine whether this conditional source view is a viable printer producer. A full-domain exclusion requires all 4,096 exact P12 parents; 16/4,096 is an early rigorous milestone, **not** the final missing K04 recovery.



## 28 November ~11:42 UTC — 208 consecutive exact source-empty P12 parents

Four additional non-overlapping original-source lanes completed [16,32), [32,48), [48,64), [64,80), followed by another four [80,112), [112,144), [144,176), [176,208). All use the **same untouched later PS-0417 REQUESTED3 little/BA packet**, exact xoroshiro128++ inverse condition, full original K04 commitment for any compatible state, and source/circuit/view/geometry-fingerprinted private ledgers. The independent domain-tree auditor has now executed over the entire **contiguous [0,208) parent interval** and returned:

| Exact proof field | Audited count |
| --- | ---: |
| Distinct P12 parents included | 208 |
| **P12 parents fully exhausted and source-empty** | **208** |
| P12 parents still unresolved or unvisited | **0** |
| P16 children examined | 3,328 |
| P16 terminal UNSAT without a model | 3,071 |
| P16 UNKNOWN, all subsequently subdivided | 257 |
| P20 grandchildren examined | 4,112 |
| P20 terminal UNSAT without a model | 4,111 |
| P20 UNKNOWN, subdivided through P22 | 1 |
| P22 great-grandchildren examined / terminal UNSAT | **4 / 4** |
| Missing required descendant receipts | 0 |
| Source-compatible 128-bit states anywhere in this exact subtree | **0** |
| Original complete K04 SHA acceptance hits | **0** |

This improves certified conditional K04 source-state exclusion from 16 to **208/4,096 P12 parents (5.08% of the initial-a state domain)** in the previously untested later-first little/BA serializer. The other 3,888 parents remain unresolved by this *exact* proof; a separate 2,555-parent P12 first-SAT first pass does not change that bound, because nearly all of its calls returned UNKNOWN. The conditional xoroshiro128++ printer hypothesis is **not** yet globally falsified; no physical coupon or original key component has been recovered.

Four further disjoint P12 exact-closure lanes have begun [208,240), [240,272), [272,304), [304,336), with local private ledgers. Aggregate proofs for later progress should replace these coverage numbers only after running the same full-domain auditor, not by counting launched workers, solver calls, or terminal timeouts.



## 28 November ~11:48 UTC — audited source-empty prefix extends to 336 parents

The next four original-source disjoint [208,240), [240,272), [272,304), [304,336) lanes have all completed, with exact recursive refinement and unmodified original K04 acceptance-first checking. The local confidential [independent full-domain auditor](../agents/agent8/k04_reverse_proof_audit.py) now certifies **336/336 consecutive P12 parent labels 0..335 are source-empty** under the conditional PS-0417 REQUESTED3 little/BA xoroshiro128++ model:

- **5,376 P16 children visited:** 5,058 terminal no-state UNSAT, 318 UNKNOWN all refined.
- **5,088 P20 grandchildren visited:** 5,087 terminal no-state UNSAT, one UNKNOWN refined.
- **Four P22 great-grandchildren:** 4/4 terminal no-state UNSAT.
- **336/336 parents entirely exhausted; zero missing descendants, zero retained compatible source states, zero original full K04 commitment hits.**
- Remaining **3,760/4,096 P12 parents have not been proved empty** by this exact tree and must not be generalized into a generator-wide exclusion.

A dedicated actual source-private firstpacket **big/BA** state-positive replay in separate [results/h17-k04-bigba-forward177-statepositive-replay-20261128.md](h17-k04-bigba-forward177-statepositive-replay-20261128.md) independently recovered the known single complete state in parent1371 and ran 177 original-commitment checks including 33 newly covered late offsets, all negative; that positive state is a different firstpacket/output layout, *not part of this laterfirst little/BA no-state prefix*. Critic's recommendation to spend compute on state-positive complete coupons was followed; source-compatible state evidence must not be collapsed into a source-empty parent count.

The final four short [336,352), [352,368), [368,384), [384,400) exact parent-domain lanes are active; their outcomes must be measured from private receipts rather than inferred from launch. K04/K08 remain MISSING, six slots PASS, combined INCOMPLETE.


## Final Agent8 lease-stage closure, 28 November ~11:50 UTC — 400 parent groups

The four final source-private original laterfirst little/BA lanes [336,352), [352,368), [368,384), [384,400) finished before the 70-minute lease-release threshold. They used the exact same unchanged pinned original files, source-conditioned model, disjoint P16→P20→P22 refinement and full K04 acceptance-first reducer. The [independent private-domain audit](../agents/agent8/k04_reverse_proof_audit.py) now certifies the entire **400 consecutive P12 parents [0,400) fully source-empty**, with **zero unresolved/missing descendants** and **zero source-compatible models**:

| Exact source-domain result | Final |
| --- | ---: |
| Disjoint P12 initial-a parent labels exhaustively checked | **400/4,096** |
| Fully empty parent labels | **400** |
| Unresolved parent labels inside [0,400) | **0** |
| P16 source-conditioned children | 6,400 |
| Terminal no-state UNSAT P16 children | 6,072 |
| P16 UNKNOWN children, all exactly refined | 328 |
| P20 children under P16 UNKNOWN branches | 5,248 |
| Terminal no-state UNSAT P20 children | 5,247 |
| P20 UNKNOWN children, exactly refined | 1 |
| P22 children under that P20 UNKNOWN | **4/4 UNSAT** |
| Cached compatible full states / original K04 commitment hits | **0 / 0** |
| Private original K04 component-hit escrow present | **No** |

**Scope limit:** this proves exact source emptiness of **400/4,096 (9.77%)** of the initial-a state domain for **later REQUESTED3 little/BA xoroshiro128++**, not the other 3,696 parent labels, not any other generator or printer serialization, and not the missing selected ACK2. The separate [earlier REQUESTED1 big/BA actual state-positive replay](h17-k04-bigba-forward177-statepositive-replay-20261128.md) found one compatible model and full original acceptance MISS over 177 whole-coupon windows, including 33 newly examined late positions; it is not a source-empty result and must not be added to the 400.

The low-yield unanchored P12 first-SAT pass was stopped after 2,555 parents (2,539 UNKNOWN, 16 UNSAT). The live exact proof workers all completed their planned bounded 400-parent scope; no source scan remains running for this invocation. The complete component key remains **INCOMPLETE** with original six accepted slots PASS and K04/K08 MISSING. Future researchers should prioritize actual complete source-model candidate production and source-fixed K08 authorial wording, not treat a conditional no-state prefix as recovered archive material.

## Boundaries and decision

A positive hit would establish a full 16-byte component matching the unchanged K04 acceptance, not automatically authenticate the speculative generator's historical use. A timeout or source-free positive cannot count as an original recovered component. The exact historical issuer and retry-state relationship remain unverified.

This execution opens a **distinct actual original-source later-first little/BA route** and produces a full-byte-slip, target-first, privately resumable recovery engine. K01/K02/K03/K05/K06/K07 remain PASS; K04 and K08 MISSING; combined REC8/1 remains INCOMPLETE.

**Primary next step:** apply source-independent P16 or another mathematically sound inversion improvement only where it increases recovery reachability on synthetic planted states; preserve all actual original SAT-state candidates and evaluate complete K04 commitments before any attempt1 holdout filter. Do not re-scan Agent1's forward big/BA or Agent13's later-first big/AB lanes.