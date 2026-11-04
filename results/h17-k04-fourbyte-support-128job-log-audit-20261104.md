# K04: completed 128-job four-byte support audit, without recomputation

**Agent 13 | 4 November 2026, ~16:30 UTC | independent log reconciliation of Agent7's completed campaign**

## Why this audit was necessary

[Agent7's manual original computation run 41838591961](https://github.com/FlareZ123/workplace-v2/actions/runs/41838591961) finished all 128 matrix jobs successfully by 15:10 UTC. However, the automatic consolidation job [41855011252](https://github.com/FlareZ123/workplace-v2/actions/runs/41855011252) failed on a GitHub-job-log endpoint redirect with HTTP 401, leaving no complete 128-job report. The [15:40 Critic intervention](../communications/broadcast/20261104T1540Z_Critic_crossarchive-authoring-and-128job-audit.md) correctly warned against treating the earlier individual shard example as full coverage. This audit reads the **finished** original logs through the GitHub Actions job-log connector. It **does not rerun even one candidate digest**.

The original finite test, authored by Agent7, enumerated **1,713 previously untested arbitrary four-whole-byte supports** relative to the copied \`PS-261003-0417\` ACK2 payload. Each support exhausts all \`2^32\` value combinations, XORs the unchanged K04 route mask, and checks the unchanged complete SHA256 commitment. Source code: [Agent7's original SFT](../agents/agent7/k04_remaining_fourbyte_supports_sft.cpp).

## Exact independent reconciliation

Read the \`list_workflow_jobs\` pages 1–5 for run \`41838591961\`, using **30 returned entries per page**, with all job IDs and conclusions from the same completed run. Read the actual saved \`get_job_logs(job_id, return_content=true, tail_lines=120)\` for **all 128 distinct successful jobs**. The readable logs contain original source control, a \`QUARTET_DONE\` record for each support, and a final \`SHARD_COMPLETE\` record.

For every job named \`full-fourbyte (s)\`, independently check:

1. Exactly one \`SHARD_COMPLETE shard=s\` with \`original_hits=0\`, and \`quartets=plants\`.
2. Every \`QUARTET_DONE q=k\` has \`complete_checks=4294967296\`, \`original_hits=0\`, \`plant_hits=1\`.
3. The **complete exact set** of logged quartet indices equals \`{s+128n | 0 <= s+128n < 1713}\`. This checks for missing or duplicated support lines, rather than trusting the summary count.
4. Each shard's declared complete checks equal \`quartets*4294967296\`; no \`ORIGINAL_K04_MATCH\` indicator occurs.
5. Across the nine independent batches of 12–18 log reads, all **128 shard IDs 0..127 appear exactly once**. No failed parsing, mismatch or missing shard was found.

Independent final audit arithmetic:

| Reconciled property | Result |
| --- | ---: |
| Completed original job logs retrieved | **128 / 128** |
| Exact shard IDs covered | **0..127, unique, no omissions** |
| Distinct enumerated four-byte supports covered | **1,713 / 1,713** |
| Full original K04 SHA256 comparisons | **7,357,278,978,048** |
| Original K04 commitment hits | **0** |
| Per-support planted positives | **1,713 / 1,713** |
| Per-shard parsing/coverage failures | **0** |

The per-shard counts were calculated from actual retrieved \`QUARTET_DONE\` and \`SHARD_COMPLETE\` lines, not inferred from the GitHub Actions \`success\` status alone. As a concrete specimen, [job 126603907384](https://github.com/FlareZ123/workplace-v2/actions/runs/41838591961/job/126603907384) logged 14 complete supports, 60,129,542,144 checks, zero original hits, 14 planted positives, and \`SHARD_COMPLETE shard=6\`. The audit establishes the corresponding proof for every shard.

## What this establishes

The 1,713 newly audited four-byte positions complement Agent7's already tested 91 leading-A9A9 positions, 12 other contiguous four-byte positions, and four prior one-byte-per-word common-lane positions. Under the original Agent7 support-partition assertions, the prior 107 and these 1,713 supports cover **all 1,820 choices of four byte positions out of 16**. Therefore **no K04 value obtainable by changing at most four entire bytes of the copied 18:02 payload passes the historical K04 commitment**, conditional on the original fixed route mask and correct exhaustive per-support algorithm. The lower bound of **five changed bytes** applies to the hypothetical physical payload relative to the particular suspect copied buffer and does not assert which five bytes are wrong.

It supplies **zero independently authentic original physical coupon bits** and no K08 terminal normalized words. It cannot establish any byte of a physical coupon if the copied payload is wholly fabricated, subject to an unrecorded writer transformation or not actually the selected stage. This is a finished finite copied-byte exclusion, best used to retire remaining four-byte radius repeats and pivot to an independently evidenced selected-stage generator/copy witness. Original official verifier, resources, commitments and candidate remain unchanged; six accepted slots remain PASS, K04/K08 MISSING, REC8 combined INCOMPLETE.

## Reconciliation method for future reuse

The GitHub Actions job-log connector returned the saved content successfully, whereas the earlier REST redirect downloader raised 401. For later expensive matrices, upload machine-readable per-shard summaries as Actions artifacts before completion and audit the saved job logs only when needed. The audit was conducted entirely by reading immutable finished logs; no new workflow was dispatched and none of Agent7's 128 jobs was rerun.
