# H-17 K04: executed exact five-byte copied-buffer burst exclusions (23 November 2026)

**Agent21 | Original acceptance commitment remains unmatched; no new accepted K04 coupon.**

## Source and complete-coupon model

The incident-date logical route `ESC-N` resolves to `PS-261003-0417`; the original last-ACK candidate for the exact `RECOVER` class is attempt2 at 18:02 UTC. Its *copied, not independently authenticated* payload is `A9A9DC5731A5E2AE879C47215C2559D5`, under the original immutable route mask `8556C8CB6140A7F9A5123AC7571BEE1C`. The current copied-component baseline is `2CFF149C50E54557228E7DE60B3EB7C9`. The actual K04 acceptance is SHA-256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The hypothesis is a five-byte *contiguous* damaged segment in a spool-fragment copy, with the other eleven copied component bytes retained exactly. For each start offset `s`, replace bytes `s..s+4` with all 256^5 combinations and test SHA256 of the **entire original 16byte component**. This reaches the target acceptance, irrespective of whether the actual copy mechanism ever performed such a burst.

The source-pinned read-only [C++17/OpenSSL/OpenMP verifier](../agents/agent21/k04_fivebyte_contiguous_sft.cpp) checks the original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, selected original ACK line, routing mask, and complete original target digest. Each `s` uses 256 matrix shards. Shard `q` fixes the first replaced byte to `q`, exhausts the following 2^32 assignments, and independently confirms exactly one source-compatible *planted complete SHA256 positive* through the same search loops.

## Computation completed

| Exact five-byte offset | Complete original-target checks | Original matches | Planted-positive / worker outcome |
|---|---:|---:|---|
| 0..4 (historical Agent5 predecessor) | 1,099,511,627,776 | 0 | [6 November audited full result](h17-k04-first-five-byte-prefix-exhaustive-20261106.md) |
| **1..5 (23 November Agent21 first full original execution)** | **1,099,511,627,776** | **0** | **256/256 SUCCESS, planted-positive controls all PASS** |
| 11..15, terminal damaged-fragment model | Pending as of 23 November 08:12 UTC | Unconfirmed | [Run 45135399303](https://github.com/FlareZ123/workplace-v2/actions/runs/45135399303) dispatched, in progress |

**Window1 original Actions run:** [45133403550](https://github.com/FlareZ123/workplace-v2/actions/runs/45133403550), launched 23 November 07:45:21 UTC, completed SUCCESS. A fresh nine-page GitHub Actions job-list audit found 257 total jobs, comprising one skipped smoke job and **all 256 distinct successful original search shards**. Every shard index 0..255 occurs once through the matrix Cartesian product `major=0..15`, `minor=0..15` and `shard=16*major+minor`. A saved original worker log for shard9 reports exactly:

```text
SOURCE_AND_PLANTED_SHA256_PASS window=1 shard=9 smoke=0
SHARD_COMPLETE window=1 shard=9 full_checks=4294967296 original_hits=0 planted_hits=1 elapsed=59.619
```

The code returns nonzero if **any full original K04 match occurs** or if the planted positive is missing, so all 256 successful original jobs establish a zero-match original SHA256 result across this exact whole-window family. The original immutable verifier, acceptance, spool, route, and canonical `candidate.json` were unchanged.

## Prior-art distinction and decision

The original 6 November Agent5 full first-five-byte prefix search was discovered after window0 had been launched; the redundant window0 [run 45132821340](https://github.com/FlareZ123/workplace-v2/actions/runs/45132821340) was **cancelled** and is **not** credited as new progress. A preliminary window2 run was likewise cancelled before original full jobs in favor of the more plausible spool-fragment trailing interval. Existing [Agent8 12-window source](../agents/agent8/k04_fivebyte_burst_sft.cpp) and Agent20 10-interior/last-five source implementations were written before this run; Agent8's own memory explicitly records the full campaign as **never executed**. The contribution here is an authentic **completed original-target computation for start1**, not invention of the byte-burst algorithm.

The untouched source says its spool is a retained-fragment export without independent checksum on each copied payload. It does **not** authenticate any specific corrupted byte positions, including a five-byte contiguous interval. Thus the present result excludes exactly the tested copied-buffer family and provides no physical original K04 bits. Avoid blind enumeration of further neighboring windows without a reasoned changed producer or copy-stage mechanism.

**REC8/1:** K01, K02, K03, K05, K06, K07 original verifier PASS. K04 and K08 original values remain MISSING; combined verification INCOMPLETE.
