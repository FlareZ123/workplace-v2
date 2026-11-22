# K04 MT lane-mosaic: independent validation and source-stage limits

**Date:** 2026-11-22  
**Reviewer:** Agent 18  
**Scope:** Independently validate the empirical MT19937 lane-mosaic discovered in `agents/agent19/k04_mt_witness_lane_mosaic_sft.py`. This is a historical-data analysis only; no facility equipment or live service was accessed.

## Decision

The raw spool payload sequence contains a statistically unusual MT19937-like recurrence pattern. Retain it as a real empirical feature of the surviving spool data. Do **not** treat the current lane-mosaic as a K04 producer: its holdout matches collapse to one dependent motif, the target is not linked to a global stage map, and no candidate passes the original K04 commitment under the tested serializer and indexing families.

The missing evidence is not another byte-order guess. It is the native PS-0417 attempt-2 job/render or a source-authenticated queue/host manifest that establishes the payload's native word order and the generator's stage/call schedule.

## Source and pinned target

- Input: `resources/evidence/print/spool-reconstruction.log`.
- Route: `resources/evidence/recovery-routing.json`, K04. The selected record is PS-261003-0417, attempt 2, `STATE=ACK`, `CLASS=RECOVER`, `DEST=bench`, at raw row 129.
- Route mask: `8556C8CB6140A7F9A5123AC7571BEE1C`.
- Original K04 commitment: `resources/acceptance.json`, slot SHA-256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.
- Target row 129 was excluded from witness discovery and candidate generation. It remains present in the source log but is not used as a training payload.

## Independent reproduction of the lane-mosaic

Using little-endian 32-bit words in forward order, each payload word was untempered as an MT19937 output-state word. For each candidate witness `(r,p,k,i,l,q)`, the exact recurrence tested was:

```text
native[l][q] == native[k][i] XOR twist(native[r][p-1], native[r][p])
```

with `r < k < l`, `p ∈ {1,2,3}`, and `i,q ∈ {0,1,2,3}`. Here `p` is the **right input lane** of the pair `(p-1,p)`. The correct source-stage interpretation is `S_k-S_r = 396+p-i` and `S_l-S_r = 623+p-q`. Equivalently, if `p0=p-1` denotes the **left input lane** (`p0 ∈ {0,1,2}`), the same equations are `S_k-S_r = 397+p0-i` and `S_l-S_r = 624+p0-q`. Agent9's C++ implementation stores this left-lane index, so its `397+p0-i` / `624+p0-q` formula is already correct. The former report formula incorrectly applied the left-lane coefficients to the right-lane variable and was one too high in both offsets.

Independent reproduction gives:

- **25** exact historical witnesses;
- **23** unique signatures `(k-r,l-r,p,i,q)`;
- raw-row geometry pairs `(52,83)`, `(53,83)`, `(53,84)`, `(53,87)`, and `(54,84)`;
- target lane candidate counts **(4,5,6,8)**, or **960** complete four-word combinations;
- **zero** K04 commitment matches among those 960 combinations.

The original discovery/reproduction program is `agents/agent19/k04_mt_witness_lane_mosaic_sft.py`.

### Independent lane-index regression

Agent18 independently regenerated the seeded MT19937 fixture using seed `0x17A11CE` and 1,400 outputs, untempered the outputs, and verified the recurrence at source positions for all three right-lane choices. For `i=q=p-1`, both conventions yield offsets `(397,624)`; incorrectly substituting right-lane `p` into the left-lane expression yields `(398,625)`. Agent18 then independently re-parsed the pinned spool SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, skipped row129 before payload decoding, rediscovered all 25 witnesses / 23 signatures, and confirmed right/left equivalence plus the old +1 error for every tuple. The independent regression is `agents/agent18/k04_mt_lane_index_independent_sft.py`.

Using the corrected right-lane equations, an independent integer MILP with 133 row-draw variables, ACK bounds [6,9], and REQUESTED rows128/130 fixed to zero gives the target cumulative-stage interval **942–955**. Repeating the 23 target-signature feasibility checks with ACK bounds [4,100] gives **0/23 feasible**. The correction changes no witness, candidate, commitment, or acceptance result.

## The four leave-one-out matches are one dependent motif

The reported four exact heldout word matches occur only at raw rows 92 and 96:

| Holdout | Job | Metadata | Matching lanes |
|---:|---|---|---|
| 92 | PS-261003-0392 | RECOVER / desk / attempt 1 ACK | 2, 3 |
| 96 | PS-261003-0396 | RECOVER / store / attempt 1 ACK | 2, 3 |

They reduce to two signatures, each observed exactly twice:

- `(54,84,p=1,i=1,q=2)`, from triples `(r,k,l)=(8,62,92)` and `(12,66,96)`;
- `(54,84,p=2,i=2,q=3)`, from the same two triples.

The two triples are exact +4-row shifts. In each single-row leave-one-out test, the other row's triple is the only witness that supplies the matching template. When both rows 92 and 96 are removed jointly from witness discovery, neither row has a matching lane. The signatures do not predict any other destination in rows 84–127. Thus 4/49 is **not four independent validations**; it is one repeated two-row motif.

### Packet-preserving null

For the little-endian/forward view, 1,000 permutations were run under each of three nulls, keeping each 16-byte packet intact and withholding row129:

1. global payload-to-row shuffle;
2. shuffle within `CLASS×DEST`;
3. shuffle within `CLASS×DEST×ATTEMPT×STATE`.

Observed: 25 witnesses, 23 signatures, 4 heldout word matches on 2 rows, and 2 repeated signatures.

| Null | Mean witnesses | 95th percentile | Maximum |
|---|---:|---:|---:|
| Global | 8.38 | 14 | 18 |
| CLASS×DEST | 10.08 | 15 | 20 |
| Full metadata | 10.05 | 15 | 18 |
| Job-suffix mod 4 | 8.39 | 13 | 19 |
| CLASS×DEST×job-suffix mod 4 | 12.85 | 18 | 22 |

The two additional phase-preserving nulls retain each packet's job-suffix residue modulo 4; the final null also retains CLASS×DEST. Across all **5,000 full-log trials** there were **zero** exact leave-one-out word matches and **zero** repeated signatures. Fixed Python RNG seeds were 20261122 through 20261126 in table order. These full-log nulls include late cross-route rows131/132. For the K04-relevant ordinary-only sequence (rows0–127), I also ran 1,000 trials each of global, CLASS×DEST, and CLASS×DEST×job-suffix-mod-4 shuffles. Observed ordinary-only: 23 witnesses / 21 signatures / 4 matches on rows92/96. Null summaries: global mean7.775, p95 13, max17, zero matches; CLASS×DEST mean9.196, p95 14, max19, zero matches; CLASS×DEST×mod4 mean12.041, p95 17, max21, with 2/1,000 trials producing four matches on two rows and repeated signatures (maximum four matches). Thus the ordinary-only motif is unusual (about 0.2% under the strict phase+metadata null), but not impossible. Seeds 20261127 through 20261129 in the same order. The result remains one dependent two-row motif, not four independent validations.

## Selected-job and metadata controls

Applying all 23 forward-view templates to the other PS-0417 records gives no exact native-word matches:

- raw row 117: attempt 1 ACK, LABEL / bench;
- raw row 128: attempt 1 REQUESTED, RECOVER / bench;
- raw row 130: attempt 3 REQUESTED, RECOVER / bench.

The only witness whose destination row has the target's exact `RECOVER / bench / attempt 2 ACK` metadata is row 132 (PS-0420), but the print-fleet crosswalk identifies PS-0420 as WATCH-SPARE, a separate route. It is not a K04 selector. It is a single lane-3 witness, signature `(53,87,p=1,i=3,q=3)`, using donors rows 45 and 98; applying it to row129 uses donors 42 and 95. It supplies lane 3 only, and its predicted lane does not equal the logged row129 payload lane.

## Source-stage graph and draw-count checks

Each witness implies the cumulative-stage equalities above. Converting the 25 full-log witnesses into a weighted graph over 133 raw rows produces **97 connected components**, with largest component size **5**. There are no contradictory cycles, but target row129 is isolated (degree zero). Because late rows131/132 are separate routes (PS-0448 ESC-S and PS-0420 WATCH-SPARE), I also reran the graph on ordinary-only rows0–127: 23 witnesses / 21 signatures, 101 components, largest size 5, and target row129 remains isolated. The ordinary-only signatures give target lane candidate sizes (3,5,6,7), or 630 complete combinations, with zero K04 commitment hits. All 21 ordinary-only target signatures are feasible under broad integer per-row draw bounds [4,12], but none under the narrower [6,9] bounds; the latter are assumptions, not a source rule. Thus the broad schedule does not rule out the ordinary-only templates.

A source-only fixed draw-count model also fails:

- constant draw count per `CLASS×DEST` (9 parameters): rank 9, least-squares residual norm 30.54, maximum absolute residual 14.27;
- `CLASS×DEST×ATTEMPT×STATE` categories: rank 10, residual norm 14.69, maximum absolute residual 5.59;
- additive base + CLASS + DEST + job-suffix-mod-4 effects: residual norm 28.07, maximum absolute residual 10.29.

These are not exact stage schedules. An exploratory integer/linear feasibility check with 133 integer per-row draw variables, ACK rows bounded in [6,9], and REQUESTED rows128/130 fixed to zero leaves the target cumulative stage between **942 and 955** under the corrected right-lane equations. The previously reported 943–957 interval used the right-lane variable with the left-lane coefficients. The corrected interval still includes the separately hypothesized p951 alignment but does not single it out; the bounds are assumptions, and the stage is not unique. Bounds [6,8] with REQUESTED rows fixed at zero are infeasible. A stronger but conditional target-consistency check added each of the 23 full-log signatures' two interval-sum equations to the 50 historical constraints. With integer per-row draws, REQUESTED rows128/130 fixed at zero, and every payload-bearing ACK row required to consume at least four 32-bit payload words, none is feasible even with upper bounds of 100 draws per row. This exclusion depends on treating the late cross-route PS-0448/PS-0420 witnesses as part of the same global stream. It is not decisive for K04 unless that shared-stream assumption is source-authenticated. On the ordinary-only 21-signature set, all templates are feasible under broad [4,12] bounds; the stage remains underdetermined. A more flexible per-row schedule should not be fitted post hoc without a source rule.

## Bounded serializer and indexing checks

- **48 fixed serializers:** all 24 permutations of four 32-bit words × both uniform byte orders were tested using the full log. Zero K04 commitment hits. The maximum was 31 witnesses / 29 signatures (little-endian permutation `(3,0,1,2)`) and 2,310 complete candidates. Repeating the 48-view search with only ordinary rows0–127 as training also gives zero hits; its maximum is 27 witnesses / 25 signatures and 1,296 candidates (little-forward: 23/21 and 630 candidates). Selecting the maximum after 48 views has a look-elsewhere cost; it is not a source-authenticated serializer.
- **Reversed-word control:** little-endian reversed order gives 23 witnesses / 22 signatures, 2 heldout matches at rows 111 and 113 (one repeated +2-row motif), 840 target candidates, and no commitment hit. Both big-endian standard views give zero witnesses.
- **Mask-first control:** applying the K04 route mask to every historical payload before MT untempering yields zero witnesses across the 48 fixed serializers. The observed MT-like structure is in the raw payload representation, not the already-XORed coupon representation.
- **ACK-only sequence:** filtering to `STATE=ACK` gives 131 rows and moves the selected attempt-2 ACK to ACK-only index 128. It reproduces 25 witnesses / 23 signatures and candidate counts (4,5,6,8), but still produces zero K04 commitment hits. The late-control geometry changes (including `(53,85)`); no solution results.

No arbitrary mixed-endian, per-row word permutation, or unconstrained gap sweep was attempted.

## Interpretation and next useful evidence

The data support an MT-like temporal mechanism in the historical raw payloads, but do not identify how the spooler interleaved payload words, metadata draws, requests, and retries. The empirical witnesses do not determine a global stage map, the holdout motif is dependent, and all bounded complete-coupon candidates fail the original commitment.

The next discriminating input is the **native PS-0417 attempt-2 spool/render and its queue/host manifest or generator configuration**, preserving original bytes and the link between job, attempt, route and output. Without that source-authenticated ordering/stage rule, do not promote an MT candidate or expand into arbitrary serializer/gap families.

**Status:** historical MT-like structure observed; source-stage identity unresolved; K04 coupon **not recovered**; original K04 commitment **not passed**.
