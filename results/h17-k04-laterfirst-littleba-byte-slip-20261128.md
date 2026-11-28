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


## Boundaries and decision

A positive hit would establish a full 16-byte component matching the unchanged K04 acceptance, not automatically authenticate the speculative generator's historical use. A timeout or source-free positive cannot count as an original recovered component. The exact historical issuer and retry-state relationship remain unverified.

This execution opens a **distinct actual original-source later-first little/BA route** and produces a full-byte-slip, target-first, privately resumable recovery engine. K01/K02/K03/K05/K06/K07 remain PASS; K04 and K08 MISSING; combined REC8/1 remains INCOMPLETE.

**Primary next step:** apply source-independent P16 or another mathematically sound inversion improvement only where it increases recovery reachability on synthetic planted states; preserve all actual original SAT-state candidates and evaluate complete K04 commitments before any attempt1 holdout filter. Do not re-scan Agent1's forward big/BA or Agent13's later-first big/AB lanes.