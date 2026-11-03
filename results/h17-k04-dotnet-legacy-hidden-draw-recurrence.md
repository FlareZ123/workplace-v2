# K04 source-only .NET Framework byte-stream producer falsifier, hidden packet draws

**Agent 2, 3 November 2026.** A fresh producer architecture was evaluated, conditional on a continuous .NET Framework `System.Random(seed).NextBytes` stream. With up to **16 unrecorded output bytes per boundary**, the earliest eight intact ordinary print packets admit **zero** source-compatible layouts. The original selected K04 ACK2, mask and SHA256 commitment are entirely excluded from this source-fitting test. No selected coupon bit was recovered.

## Distinct hypothesis

A printer host built on an older C#/.NET runtime might generate each 16-byte opaque spool PAYLOAD by calling legacy `System.Random(seed).NextBytes`. The historical H-17 print-host software and RNG are **not authenticated** by the surviving source, so the model is exploratory. Crucially, it is mathematically different from previous MT19937, PCG and xorshift production models. It could produce a complete missing print payload **only if a continuous source-compatible generator state/chronology existed**.

Microsoft's [legacy reference-source `Random.cs`](https://github.com/microsoft/referencesource/blob/main/mscorlib/system/random.cs) defines a 55-cell subtractive generator, with each successive byte `InternalSample() % 256`, cell index `inext` advancing one and `inextp` displaced 21 cells. For any output stream, once at least 55 bytes have passed, raw output samples obey
`R[t] = (R[t-55] - R[t-34]) mod (2^31 - 1)`
(with the special all-`MBIG` edge handled in the implementation). Because `2^31-1 ≡ -1 mod 256`, every output byte necessarily satisfies `B[t] ∈ {(B[t-55]-B[t-34]) mod256, (B[t-55]-B[t-34]-1) mod256}`. This is a **seed-independent necessary condition** on any three *observed* output bytes at these offsets, even when other stream values are unavailable. It provides a stringent architecture test without a seed search.

## Source-selected chronology search

Use the original printer file SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Select the **first eight** regular 16-byte source records in printed 07:00..07:35 order, with no disputed ESC-N target involved. Preserve all 16 bytes within each packet in source order. Between adjacent packets, grant an arbitrary unobserved gap of 0..16 generator byte samples. The starting prelude may be arbitrary: the local triple rule is invariant to absolute stream offset once output history is established.

There are `17^7 = 410,338,673` possible seven-gap vectors. A depth-first sieve abandons a partial vector as soon as a three-observed-byte recurrence is violated, so it need inspect only **1,480** partial nodes. **Zero** complete gap vectors satisfy the first eight original source packets. In fact the fifth packet already rules out every 0..16-gap continuation; the full eight-record run confirms the exact prescribed scope.

The local original gap-free screen independently found **19/1,993** compatible byte triples under the known 55/34 indices, against the necessary perfect compatibility of a continuous legacy `NextBytes` generator. This is a scoped diagnostic, not a probabilistic proof about alternative generators.

## Positive controls and reproducibility

The [portable standard-library SFT](../agents/agent2/k04_dotnet_variable_gap_sft.py) reproduces the legacy initializer and byte generator directly from Microsoft's published reference code. Four seeds (0,1,42,2147483647) each pass all 945 lag55/34 necessary relationships in a 1,000-byte synthetic stream. An independent seeded synthetic 8-packet source with true hidden gaps `(2,0,3,1,4,2,1)` is recovered by the same gap sieve **exactly once**, visiting 1,599 partial nodes. The original intact source returns zero candidates, with program assertions checking the complete result and positive control.

Local source-equivalent run on 3 November:
```text
source_nodes_visited=1480
source_compatible_gap_vectors=0
synthetic_source_nodes_visited=1599
synthetic_compatible_gap_vectors=1
actual_planted_gaps_recovered=true
```

## Recovery consequence and limits

This **excludes the original first eight regular packets as one continuous legacy `System.Random.NextBytes` byte stream with zero-to-sixteen hidden draws between source packets**, regardless of original integer seed or unknown prelude. The source could still involve per-job reseeding, more than sixteen hidden samples between packets, alternative byte packing, multi-stream interleaving, a modern `Random` implementation, or a different producer entirely. For example, at gap allowance up to 20, some partial eight-record source layouts survive necessary constraints; these have not been authenticated and do not imply a predictor.

The experiment isolates a new producer class and its exact stop condition before testing the K04 commitment or manufacturing a selected coupon. No original K04 bit or K08 word was established. The six preexisting individual slots remain the only confirmed PASS components, and combined REC8 remains INCOMPLETE. Further .NET work needs a source-tied producer or explicit draw-count witness, rather than expanding unconstrained gaps.
