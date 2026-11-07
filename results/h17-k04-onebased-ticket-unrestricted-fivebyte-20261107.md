# H-17 K04: complete unrestricted five-ticket *one-based* byte repair, negative

**Agent 4 | 7 November 2026 | 128/128 completed original-target shards, 1,099,511,627,776 full SHA256 comparisons, zero original hits; 128/128 planted complete positives.** The original six independently accepted slots remain PASS, K04 and K08 remain MISSING, combined REC8/1 INCOMPLETE.

## Genuine distinct search boundary

The original 4 October print-fleet return register joins `PS-261003-0417` to ESC-N / L-29/N and specifies five cabinet-service tickets **ST-094, ST-081, ST-106, ST-099, ST-112**. Treating their decimal numbers as **one-based byte ordinals modulo 16** gives `[(94-1)%16, (81-1)%16, (106-1)%16, (99-1)%16, (112-1)%16]`, sorted **[0,2,9,13,15]**. This is a speculative fault-position hypothesis: the actual ticket source is a next-day parts/returns register, not a copy-stage diagnostic or byte-indexing specification.

The previously completed 7.36-trillion-comparison [four-byte audit](h17-k04-fourbyte-support-128job-log-audit-20261104.md) excludes all at-most-four arbitrary copied-byte substitutions. Agent45 had independently exhausted a *different zero-based* service-ticket support **[0,1,3,10,14]**. Agent8's [one-based restricted prior-cache case](h17-k04-onebased-cassette-tickets-two-prior-cache-20261106.md) tested 671,088,640 assignments **only** with two source donor bytes fixed and three arbitrary bytes. Neither result covered all `2^40` combinations at the alternate one-based support. This experiment closes precisely that remaining complete family.

## Pinned original source and complete candidate

- Selected original event: `2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER`, copied opaque buffer `A9A9DC5731A5E2AE879C47215C2559D5`.
- Official route mask: `8556C8CB6140A7F9A5123AC7571BEE1C`.
- Unchanged full original K04 SHA256: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.
- Source spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; return register SHA256 `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf`.
- For each proposed physical coupon `P`, keep the **other eleven bytes** exactly as in the unverified copied ACK2; independently assign every 8-bit value at the five specified byte positions. Form `C = P XOR route_mask`, and compare **all 32 SHA256(C) bytes** to the immutable target. No sampled-prefix acceptance and no phrase or nonce assumptions.

This set consists of exactly `2^40 = 1,099,511,627,776` distinct complete 16byte coupons. It includes coupons that differ in fewer than five bytes (already excluded by the earlier fourbyte audit) but does not cover other fivebyte supports.

## Completed live GitHub computation and independent log audit

The executed C++17/OpenSSL/OpenMP [source-pinned SFT](../agents/agent4/k04_onebased_five_full_sft.cpp), source SHA256 `d671f512718fbcdcb95457364dda9fce512318a7dc7222798fa377a357d56bd4`, pinned copied row, original spool and register hashes, mask and original target. The original local source compiled and completed smoke on shard111, and the remote Git blob `c441076cd160fee26d5975b0df5148ef749215bf` was confirmed identical. The [manual 128-way partition](../.github/workflows/agent4-k04-onebased-five-ticket-full-manual.yml) was dispatched on the unmodified evidence at head `fa019264c2066c148a4444b0fc2f80141de020b2`.

**[Original successful Actions run 42323527367](https://github.com/FlareZ123/workplace-v2/actions/runs/42323527367)**, dispatched 7 Nov 01:20:24Z, completed 01:37:02Z. All **128/128 jobs SUCCESS**.

For each integer shard `s = 0..127`, the program fixes the first modified *component* byte (position0) to either `2*s` or `2*s+1`; enumerates every assignment to positions 2,9,13,15. This partitions the entire 40bit space into 128 disjoint exact `2^33=8,589,934,592`-candidate shards. It checks the SHA256 compressor against **1,024 ordinary OpenSSL SHA256 whole-message digests** per job and creates an independent planted full-coupon digest within its assigned shard, required exactly once. All eight SHA256 state words are checked for actual target matches.

**Post-run independent saved-log audit:** retrieved **all 128 distinct job IDs** across the five paginated job-list pages and read each job's own saved log with the GitHub Actions log reader in ten batches. For every job, parsed its `SHARD_COMPLETE shard=s component_byte0=[2s,2s+1] checks=8589934592 original_hits=0 plant_hits=1` marker, verified that its `SOURCE_SHA_AND_1024_WHOLE_MESSAGE_CONTROLS_PASS` line exists and its job conclusion is SUCCESS. The parsed shard IDs exactly cover **0..127 once each**, no omissions/duplicates, no parsing discrepancies or counter errors. Aggregates:

| Audited property | Actual saved-log outcome |
| --- | ---: |
| Successful original job logs and distinct shards | **128 / 128** |
| Full SHA256 original-target checks | **1,099,511,627,776** |
| Original K04 matches | **0** |
| Distinct planted complete-coupon positives | **128 / 128** |
| Source/digest/partition/log errors | **0** |

Representative original shard2 saved-log line:

```text
SHARD_COMPLETE shard=2 component_byte0=[4,5] checks=8589934592 original_hits=0 plant_hits=1 elapsed_sec=116.811
```

## Logical impact and limitation

**Exact result:** no 16byte original K04 component in this exhaustive source-conditioned support family passes the historical full 256bit commitment. Because position0 contains 256 possible component bytes across the partition, there is no undiscovered subshard of this family. The fresh negative excludes an additional entire **one-based five-ticket support** beyond the prior zero-based case and the earlier restricted two-cache model.

The one-based index operation is **not supported as an observed device error law**; a 2026-10-04 vendor return ticket does not authenticate a specific 2026-10-03 media byte location. The result says nothing about physical original coupons differing at six or more positions, at other fivebyte supports, about a full stage/issuer/copy transform, or about an unseen independent physical witness. Do not extrapolate this to a universal five-byte bound, and do not launch a mixed-base/further ticket permutation campaign without a new source-valued fault selector.

No original `resources/`, verifier, route, acceptance, or canonical candidate bytes were changed. No K04 original physical bit or K08 terminal word was authenticated. Six historical PASS unchanged; combined recovery still INCOMPLETE.
