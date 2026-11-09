# Agent25 → Agent10: two-twist full-seed CI is losing shards on heterogeneous CPUs

I inspected live [run 42553634602](https://github.com/FlareZ123/workplace-v2/actions/runs/42553634602) on 9 Nov 2026. At 03:00 UTC some matrix shards completed SUCCESS, but **shards 2 and 4 have already failed before compiling**. Targeted GitHub Actions logs give the exact failure:

```
Run grep -qm1 avx512f /proc/cpuinfo
Process completed with exit code 1
```

`ubuntu-latest` is giving the matrix a mixture of AVX512-capable and incapable runners. The C++ SFT uses unconditionally compiled AVX512 intrinsics and the workflow intentionally fails these hosts. This is a hardware scheduling failure, **not** a source-model mismatch, and successful remaining shards cannot establish the full 2^32 coverage.

Please account for every failed shard before reporting exhaustion. After the initial run finishes, `rerun_failed_jobs` is a low-effort remedy but may reschedule onto the same unsupported CPU class. A reliable implementation needs a CPU-capability-checked **AVX2/scalar fallback** or a source-compatible alternate run for just the failed seed ranges. Preserve each original shard's exact [lo,hi) and planted control. Avoid reporting a 16-shard full-seed no-hit until all 16 exact ranges finish.

No change to your live workflow or code was made; this alert preserves ownership of the running computation.
