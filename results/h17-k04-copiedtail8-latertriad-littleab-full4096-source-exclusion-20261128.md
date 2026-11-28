# K04: little-endian AB copied-tail / later-REQUESTED3 triad is source-empty over the full 128-bit state domain

**Agent 29 · 28 November 2026 · exact original-source conditional exclusion · K04 remains MISSING**

## Question

Agent 8 closed the full state domain for one precise xoroshiro128++ triad hypothesis under **big-endian / AB** serialization: treat the last eight copied bytes of disputed PS-0417 ACK2 as native output3 and the two intact words of later REQUESTED3 as consecutive outputs4/5, then reconstruct outputs2/3 as the selected coupon and apply the unchanged K04 route reduction.

The remaining conventional byte-order ambiguity for that same fixed word order was **little-endian / AB**. This run tests that disjoint source interpretation exactly. It does not fit the other eight copied ACK2 bytes.

## Frozen source hypothesis

Under xoroshiro128++ 1.0 (49,21,28):

1. Decode each 64-bit source word little-endian.
2. The physical **last eight bytes** of copied PS-0417 ACK2 are native output3.
3. The two physical 64-bit halves of intact REQUESTED3 are native outputs4 and5 in AB order, with no intervening native draw, reset or serializer change.
4. For every complete state satisfying those three full 64-bit observations, reverse three generator steps and construct the selected physical coupon from outputs2 and3 in little-endian AB order.
5. XOR that complete 16-byte coupon with the unchanged original K04 route mask and compare the full original K04 SHA-256 commitment **before** the earlier REQUESTED1 pair is used as a diagnostic holdout.

Original spool, routing and acceptance files were pinned by SHA-256. Source state and any hypothetical candidate bytes remained in owner-private local storage; no historical source computation ran in GitHub Actions.

## Exact state-space decomposition

For a fixed first observed xoroshiro128++ output and first 64-bit state word `a`, the second state word is algebraically determined. Thus every source-compatible 128-bit state is represented by one of the 2^64 values of `a`.

The same disjoint partition used by the big-endian proof was used here:

- P12 fixes state-a bits `0,1,2,3,22,23,24,25,45,46,47,48`: 4,096 exhaustive parent cubes.
- Every terminal P12 UNKNOWN is divided by bits `4,5,6,7` into sixteen P16 children.
- Every terminal P16 UNKNOWN is divided by bits `8,9,10,11` into sixteen P20 grandchildren.
- SAT states, if any, are model-blocked and acceptance-tested before a cube can become terminal UNSAT.
- UNKNOWN is never counted as exclusion.

The original run used five disjoint local workers for the P16 layer. An independent read-only audit reopened the complete private ledger, rechecked source replay, exact partition membership and the original acceptance/holdout accounting, and required every descendant of an UNKNOWN parent to exist before calling that parent closed.

## Final original-source result

| Proof depth | Exact cubes recorded | Terminal UNSAT | Terminal UNKNOWN | Complete source-compatible states |
| --- | ---: | ---: | ---: | ---: |
| P12 | **4,096 / 4,096** | **742** | **3,354** | **0** |
| P16 below every P12 UNKNOWN | **53,664 / 53,664** | **53,640** | **24** | **0** |
| P20 below every P16 UNKNOWN | **384 / 384** | **384** | **0** | **0** |
| Fully closed P12 parents after refinement | **4,096 / 4,096** | **all source-empty** | **0 open** | **0** |

Independent audit:

```text
P12_recorded=4096
P12_unsat=742
P12_unknown=3354
P16_recorded=53664
P16_unsat=53640
P16_unknown=24
P16_missing=0
P20_recorded=384
P20_unsat=384
P20_unknown=0
P20_missing=0
closed_empty=4096
closed_with_states=0
open=0
states=0
original_K04_hits=0
REQUESTED1_holdout_replays=0
```

There are **zero complete source-compatible states** in the entire 128-bit state domain for this little-endian / AB hypothesis. Consequently the model produces zero complete K04 component candidates and zero original commitment hits. The cube count must not be described as a number of SHA candidate checks.

## Material combined consequence

This closes the remaining endian ambiguity for the exact fixed-order triad model.

- Agent 8: **big-endian / AB** whole-domain source-empty proof: [full proof](h17-k04-copiedtail8-latertriad-full4096-source-exclusion-20261128.md).
- Agent 29: **little-endian / AB** whole-domain source-empty proof: this report.

Therefore **neither conventional 64-bit endian rendering can make the copied ACK2 tail plus immediate later REQUESTED3 pair a gap-free AB xoroshiro128++ output triad**. Re-running this same AB/no-gap triad with another SAT budget or merely swapping 64-bit byte order is now closed work.

This materially narrows the selected-event producer hypothesis, but it does **not** recover the physical K04 coupon. The copied ACK2 tail is still not independently authenticated as original printer output; REQUESTED3 is a request record rather than a proven media emission. Different word ordering, hidden output gaps, resets, different copied-byte integrity assumptions or a different producer remain separate models and require their own source justification.

## Reproduction

The generalized source-safe machinery already committed by Agent 8 accepts `--endian little`:

- `agents/agent8/k04_pruned_native.py`
- `agents/agent8/k04_triad_p12_source_private.py`
- `agents/agent8/k04_triad_p16_unknown_refiner_private.py`
- `agents/agent8/k04_triad_p20_unknown_refiner_private.py`
- `agents/agent8/k04_triad_exact_source_ledger_audit.py`

This execution additionally used a local assumption-session optimization to amortize sibling SMT setup; source-free planted-state controls were run before historical refinement, and the final result was checked by a separate read-only ledger audit. No private state or source-derived candidate bytes are committed.

**Official recovery state remains K01/K02/K03/K05/K06/K07 PASS; K04 and K08 MISSING; combined REC8/1 INCOMPLETE.**
