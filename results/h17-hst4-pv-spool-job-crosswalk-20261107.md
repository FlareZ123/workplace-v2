# H-17 HST-4 PV ↔ spool-job index crosswalk

**Date:** 2026-11-07  
**Status:** New source-derived structural lead. The index alignment is exact in the surviving export; a shared PRNG/interleaving interpretation remains unproven.

## Finding

The 112 HST-4 records with `field=PV` have unique, contiguous sequence values **100–211**. The first 112 spool records are the normal jobs **PS-261003-0300 through PS-261003-0411**, in that order. For every one of those 112 records:

```
spool job suffix = HST PV seq + 200
```

This gives an exact arithmetic crosswalk across two otherwise separate source files. The spool continues with normal jobs 0412–0427, while the local HST-4 PV export stops at seq 211. Under the same offset, those missing HST records would be seq **212–227**, corresponding to jobs **0412–0427**. The K04 target job **PS-0417** therefore maps to the absent HST-4 record **seq 217**.

## Evidence and row alignment

Sources:

- `resources/evidence/telemetry/freeze-export.jsonl`
- `resources/evidence/print/spool-reconstruction.log`
- `agents/agent49/k04_p951_symbolic_basis.py` (the 133 printer-payload start positions used for the p951 chronology)

The first 128 spool rows are jobs 0300–0427 in ascending suffix order. The first 112 align one-for-one with the 112 HST PV sequence values. The HST file has no PV records for 212–227.

The p951 start-position list gives a further candidate interleave: after each four-word printer payload, there is an unobserved gap before the next printer row. For the first 112 rows, there are exactly 112 such gaps. Their lengths range from 2 to 13 words and sum to 389. This is compatible with a record-generation process occurring between jobs, although it does not prove that the HST PV record consumed those words.

### Missing HST range and corresponding spool rows

The gap length is `starts[i+1] - (starts[i] + 4)`. Spool row numbers below are zero-based.

| HST PV seq | Implied job | Spool row | Payload start | Gap after payload |
|---:|---:|---:|---:|---:|
| 212 | PS-0412 | 112 | 837 | 5 |
| 213 | PS-0413 | 113 | 846 | 3 |
| 214 | PS-0414 | 114 | 853 | 4 |
| 215 | PS-0415 | 115 | 861 | 5 |
| 216 | PS-0416 | 116 | 870 | 2 |
| **217** | **PS-0417** | **117** | **876** | **4** |
| 218 | PS-0418 | 118 | 884 | 3 |
| 219 | PS-0419 | 119 | 891 | 4 |
| 220 | PS-0420 | 120 | 899 | 2 |
| 221 | PS-0421 | 121 | 905 | 3 |
| 222 | PS-0422 | 122 | 912 | 2 |
| 223 | PS-0423 | 123 | 918 | 2 |
| 224 | PS-0424 | 124 | 924 | 2 |
| 225 | PS-0425 | 125 | 930 | 2 |
| 226 | PS-0426 | 126 | 936 | 2 |
| 227 | PS-0427 | 127 | 942 | 1 |

The selected K04 copy is later in the spool log: **PS-0417 ACK2 / RECOVER**, zero-based row 129, payload start 951. The original **PS-0417 ACK1 / LABEL** appears at row 117, payload start 876. Thus seq 217, if the crosswalk is valid, belongs to the original job identity/first print occurrence; it is not a separate historian sequence for the later ACK2 retry.

## Interpretation and limits

- **High confidence:** the surviving HST PV sequence 100–211 maps arithmetically to spool job suffixes 0300–0411, with a constant offset of 200.
- **Moderate confidence:** the missing HST range 212–227 is the natural continuation of that crosswalk and includes the K04 job identity at seq 217.
- **Unproven:** the HST PV rows were generated from the same MT stream as the printer payloads, or consumed the interstitial words in the p951 chronology. The gap lengths are a useful schedule hypothesis, not proof of draw counts. One gap in the missing 212–227 run (seq 227) is only one word, so a literal one-record/one-gap draw model would need to explain that case.
- Tested simple `round(12 + 76 * random())` mappings that put the first MT word at the post-job gap positions are contradicted by printer-only parity; the pre-job gap-start version also conflicts wherever the source basis fixes the relevant high bits. A constant seven-word PV chronology was separately falsified in `results/h17-k04-pv-triad-stage7-all112-source-falsifier-20261105.md`. The new job-index crosswalk is distinct from that constant-stride model.
- This finding does not recover K04 and does not justify changing `candidate.json`.

## Highest-value acquisition

Request the original HST-4 historian export for **seq 212–227**, with **seq 217 / PS-0417** prioritized. Preserve every field and the original representations, including PV values, DIAG_WORD raw values, tag, unit, quality, state, revision, acquisition timestamp, and any source-side sample/job cross-reference. Also request the HST-4 data dictionary or acquisition log defining the meaning and scope of `seq`.

Retrieving the whole 212–227 interval is preferable to requesting seq 217 alone: it tests whether the +200 relationship continues across the full missing run and provides the adjacent records needed to establish provenance. If available, obtain the untrimmed HST-4 export around the 21:14 interruption.

## Reproduction

The core index check is:

```python
pv_seq = sorted(r["seq"] for r in pv_rows)
assert pv_seq == list(range(100, 212))

first_112_job_ids = [r["job"] for r in spool_rows[:112]]
assert first_112_job_ids == list(range(300, 412))
assert [job - 200 for job in first_112_job_ids] == pv_seq
```

For each of the first 128 spool rows, compute the interstitial gap using the `STARTS` array in `agents/agent49/k04_p951_symbolic_basis.py`. The missing seq 212–227 gap lengths are:

```
[5, 3, 4, 5, 2, 4, 3, 4, 2, 3, 2, 2, 2, 2, 2, 1]
```
