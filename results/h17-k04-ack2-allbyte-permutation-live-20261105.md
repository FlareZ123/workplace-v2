# K04 selected ACK2: unrestricted original-byte multiset permutation trial

**Agent 13 | 5 November 2026 | live run, NOT yet an exhaustive negative.**

The historical archive remains **K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined INCOMPLETE**. This is a new *complete-coupon* capture-stage search, subject to a highly speculative preservation assumption. It should not be read as recovered physical media.

## Distinct modeled copier fault

The event-selected printer copied payload is `A9A9DC5731A5E2AE879C47215C2559D5` from ESC-N job `PS-261003-0417`, RECOVER ACK attempt2 at 18:02 UTC. The custodian explicitly says ACK authenticates dispatch, not copied media. Prior exhaustive four-*changed-byte* searches prove a correct original under the unchanged mask must differ at five or more copied byte positions. A different failure mechanism could **reorder an otherwise intact byte multiset**, including more than four position changes.

The copied 16 bytes contain two `A9` values and fourteen other distinct bytes. The complete set of their unique arbitrary positional permutations therefore has **16!/2! = 10,461,394,944,000 distinct 16-byte coupons**. This source-specific permutation class includes all previous word/lane reorders (Agent5's 24^5 class, Agent9's 24^4 class) but also moves bytes *between* different 32-bit words without limits. It is disjoint in mechanism from replacing arbitrary original byte values. The source **does not attest any 16-byte permutation fault**, and this model is not intrinsically more likely than a lost original/copy stage.

For each candidate original byte permutation `P`, derive the **complete** K04 component `P XOR 8556C8CB6140A7F9A5123AC7571BEE1C`, then require the original **full** SHA256 digest `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. No original source or official verifier was modified.

## Current reproducible status

The portable [source-pinned C++17/OpenSSL SFT](../agents/agent13/k04_allbyte_permutation_sft.cpp) verifies original source SHA256 for printer, route and acceptance, reselects exactly the target ACK header/payload, and compares its optimized one-block digest with independent OpenSSL SHA256 at multiple disjoint ranks. Multiset *unranking* and lexicographic successor agree on boundary/interior positions, including final rank. A different **complete synthetic planted coupon** is chosen separately inside each shard; every shard must recover it exactly once.

Local original-source pilot: **10,000,000 complete original comparisons, zero K04 matches; synthetic exact full-coupon positive = 1**. Local `-O3` run used shard137/256 and took about half a second. An independently dispatched [GitHub Actions source checkout and pilot](https://github.com/FlareZ123/workplace-v2/actions/runs/41965553118), source commit `5975fd2`, **completed success**, raw job log confirms:

```
SHARD_COMPLETE index=137 of=256 start=5598480888000 end=5598490888000 tested=10000000 original_hits=0 planted_hits=1
```

The [manual exhaustive workflow](../.github/workflows/agent13-k04-allbyte-permutation-manual.yml) has **256 disjoint complete rank intervals**, `floor(TOTAL*j/256)` through `floor(TOTAL*(j+1)/256)`; each covers roughly 40.9 billion distinct original coupons. `fail-fast:false` means an accepted original match in one shard cannot cancel untested shards, and a matching shard emits `K04_AUTHENTIC_MATCH` with coupon and component before returning nonzero. A full run was **dispatched** on 5 November, GitHub Actions [run 41965620442](https://github.com/FlareZ123/workplace-v2/actions/runs/41965620442); **it was queued when this document was written**. Zero result for the 10.46 trillion is **not asserted** while it is incomplete.

## Decision boundary

The full outcome has two meaningful branches. Any exact original K04 match supplies a fully formed 16-byte component and must be passed through the *untouched* `verify.py` and incorporated into the combined REC8 key only after K08 is also recovered. If all 256 shards finish, every unique permutation of the copied buffer is excluded, *and nothing more*: replacement of byte values, corrupted physical paper, a different original producer, or another copied source remain open. The probe authenticates no selected physical byte absent a true SHA hit.

For run inspection, prefer GitHub Actions job status and short targeted job logs. **Do not mark this model exhausted, or infer a seventh PASS, from a queued or partial run.**
## Completed-run status reconciliation (Agent 7, 9 November 2026)

The previously pending [full exhaustive Actions run 41965620442](https://github.com/FlareZ123/workplace-v2/actions/runs/41965620442) **finished with conclusion success** at 2026-11-05 11:58:32 UTC. The Actions jobs endpoint, inspected on 9 November, returned **257 jobs, all conclusion=success**, consisting of the smoke job and the complete 256-member `exhaustive (0..255)` matrix. The workflow's exhaustive command fixes `shard_count=256` and `max_candidates=0` for every shard. The source SFT's return contract is `return hits?10:(plant_hits==1?0:5)`, where `hits` counts exact 256-bit original K04 commitment matches and `plant_hits` validates a complete synthetic positive. Therefore each successful exhaustive job establishes `original_hits=0`, `planted_hits=1`, with all nominal rank partitions covered. This is a **full-model rejection of any permutation of the exact selected copied 16-byte multiset**, assuming the workflow's checked-out SFT and standard GitHub job-exit semantics.

This reconciliation uses Actions job conclusions plus the exact workflow and source return contract; it does not claim a separately downloaded and compared set of 256 raw terminal log lines. The selected K04 remains unrecovered. No search was rerun, and no original file, verifier, route, commitment, or candidate was modified.
