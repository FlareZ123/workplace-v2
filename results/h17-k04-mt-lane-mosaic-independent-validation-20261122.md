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

with `r < k < l`, `p ∈ {1,2,3}`, and `i,q ∈ {0,1,2,3}`. The corresponding source-stage interpretation is `S_k-S_r = 397+p-i` and `S_l-S_r = 624+p-q`.

Independent reproduction gives:

- **25** exact historical witnesses;
- **23** unique signatures `(k-r,l-r,p,i,q)`;
- raw-row geometry pairs `(52,83)`, `(53,83)`, `(53,84)`, `(53,87)`, and `(54,84)`;
- target lane candidate counts **(4,5,6,8)**, or **960** complete four-word combinations;
- **zero** K04 commitment matches among those 960 combinations.

The original discovery/reproduction program is `agents/agent19/k04_mt_witness_lane_mosaic_sft.py`.

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

Across all 3,000 trials there were **zero** exact leave-one-out word matches and **zero** repeated signatures. This supports a genuine temporal MT-like structure in the raw sequence; it does not make the two-row motif independent or identify the selected target's stage.

## Selected-job and metadata controls

Applying all 23 forward-view templates to the other PS-0417 records gives no exact native-word matches:

- raw row 117: attempt 1 ACK, LABEL / bench;
- raw row 128: attempt 1 REQUESTED, RECOVER / bench;
- raw row 130: attempt 3 REQUESTED, RECOVER / bench.

The only witness whose destination row has the target's exact `RECOVER / bench / attempt 2 ACK` metadata is row 132 (PS-0420). It is a single lane-3 witness, signature `(53,87,p=1,i=3,q=3)`, using donors rows 45 and 98. Applying that signature to row129 uses donors 42 and 95. It selects lane 3 only, is a single witness, and does not supply a complete coupon. Its predicted lane does not equal the logged row129 payload lane.

## Source-stage graph and draw-count checks

Each witness implies the cumulative-stage equalities above. Converting the 25 witnesses into a weighted graph over 133 raw rows produces **97 connected components**, with largest component size **5**. There are no contradictory cycles, but target row129 is isolated (degree zero). The witness relations therefore do not determine a global MT stage map or connect the target to a historical anchor.

A source-only fixed draw-count model also fails:

- constant draw count per `CLASS×DEST` (9 parameters): rank 9, least-squares residual norm 30.54, maximum absolute residual 14.27;
- `CLASS×DEST×ATTEMPT×STATE` categories: rank 10, residual norm 14.69, maximum absolute residual 5.59;
- additive base + CLASS + DEST + job-suffix-mod-4 effects: residual norm 28.07, maximum absolute residual 10.29.

These are not exact stage schedules. An exploratory integer/linear feasibility check with per-row draws in [6,9] and REQUESTED rows consuming zero leaves the target cumulative stage between 943 and 957; the stage is not unique. Bounds [6,8] with REQUESTED rows fixed at zero are infeasible. A more flexible per-row schedule would be underdetermined without a source rule and should not be fitted post hoc.

## Bounded serializer and indexing checks

- **48 fixed serializers:** all 24 permutations of four 32-bit words × both uniform byte orders were tested. Zero K04 commitment hits. The maximum was 31 witnesses / 29 signatures (little-endian permutation `(3,0,1,2)`) and 2,310 complete candidates, still with no commitment hit. Selecting the maximum after 48 views has a look-elsewhere cost; it is not a source-authenticated serializer.
- **Reversed-word control:** little-endian reversed order gives 23 witnesses / 22 signatures, 2 heldout matches at rows 111 and 113 (one repeated +2-row motif), 840 target candidates, and no commitment hit. Both big-endian standard views give zero witnesses.
- **Mask-first control:** applying the K04 route mask to every historical payload before MT untempering yields zero witnesses across the 48 fixed serializers. The observed MT-like structure is in the raw payload representation, not the already-XORed coupon representation.
- **ACK-only sequence:** filtering to `STATE=ACK` gives 131 rows and moves the selected attempt-2 ACK to ACK-only index 128. It reproduces 25 witnesses / 23 signatures and candidate counts (4,5,6,8), but still produces zero K04 commitment hits. The late-control geometry changes (including `(53,85)`); no solution results.

No arbitrary mixed-endian, per-row word permutation, or unconstrained gap sweep was attempted.

## Interpretation and next useful evidence

The data support an MT-like temporal mechanism in the historical raw payloads, but do not identify how the spooler interleaved payload words, metadata draws, requests, and retries. The empirical witnesses do not determine a global stage map, the holdout motif is dependent, and all bounded complete-coupon candidates fail the original commitment.

The next discriminating input is the **native PS-0417 attempt-2 spool/render and its queue/host manifest or generator configuration**, preserving original bytes and the link between job, attempt, route and output. Without that source-authenticated ordering/stage rule, do not promote an MT candidate or expand into arbitrary serializer/gap families.

**Status:** historical MT-like structure observed; source-stage identity unresolved; K04 coupon **not recovered**; original K04 commitment **not passed**.
