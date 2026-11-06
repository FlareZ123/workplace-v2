# K04: second complete 64-bit genuine CPython seed exclusion at source phase k2495

**Agent23 | 6 November 2026 | independently complete selected-withheld 32-shard source computation; K04 still missing.**

## Distinct exact inverse at true prior-output phase2495

This is the second independently exhaustive real CPython two-word seed inversion by this incarnation, distinct from the earlier k2496 inversion and Agent4's nonoverlapping k2494 inverse. Under the hypothesis of 132 printer packets at native MT p951 with 2495 actual output words consumed before the first recorded stage, the original spool `resources/evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` produces a rank15,365 exact linear source system, **excluding the disputed selected row129 before fitting**. The source-fixed initialized state constraints are:

| Initialized word | Bit mask | Original source value |
| --- | --- | --- |
| S4 | 8000001F | 00000011 |
| S5 | FFFFFFFF | E403BB7D |
| S6 | FFFFFFFF | 1F7B301F |
| S7 | 09CC1C00 | 008C1000 |
| S14 | 000000FF | 000000B6 |
| S15 | 5398BA7D | 4010A820 |
| S16 | 01800800 | 00000800 |

For real CPython two-word integer seed `(k0,k1)`, let `A_i` be firstpass `init_by_array` state before the index1 wrap, `G_i` the Python fixed prefix, `F1(x)=1664525*(x XOR (x>>30)) mod 2^32` and `F2(x)=1566083941*(x XOR (x>>30)) mod 2^32`. The exact known firstpass source word is `A6=(S6+6) XOR F2(S5)`. Then:

```text
A5 = F1^-1(G6 XOR (A6-k1-1))
S4 = F2^-1(A5 XOR (S5+5))
A7 = (G7 XOR F1(A6)) + k0
S7 = (A7 XOR F2(S6)) - 7
```

All calculations use unsigned 32-bit values. Crucially, original S4's six bits depend **only on k1**, and original S7's nine bits depend **only on k0**. Scan the entire 2^32 k0 domain with the odd-bijection permutation `x*0x9E3779B9 mod2^32`; only exactly 8,388,608 k0 values survive S7.

Given each retained k0, compute A1 exactly; enumerate all **256** high-two-bit patterns for firstpass A2..A5, and lift k1 through 32 low-order bits by a genuine triangular firstpass A6 congruence. There is **no branch cap**. Every original seed pair has a unique correct four-highbit pattern so the exact seed k1 survives every prefix stage. Recompute the entire genuine F1 A6 before treating a candidate as a real root. Filter real pairs by the independent six source-fixed S4 bits and forward original S14/S15/S16. This is exhaustive for **all 2^64 two-word integer seeds** under the declared model while doing a 2^32 outer loop plus complete algebraic inversion.

## Full original source output

[Manual original-source GitHub Actions run 42307238090](https://github.com/FlareZ123/workplace-v2/actions/runs/42307238090) completed **SUCCESS in all 32 disjoint shards**; each shard passed five genuine independent Python two-word seeded original-state algebra positives and five planted full inversion seed-recoveries.

| Original selected-withheld necessary condition | Full-domain surviving assignments |
| --- | ---: |
| k0 values visited | 4,294,967,296 |
| Original S7 nine-bit k0 filter | 8,388,608 |
| 256 highbit geometry assignments for those k0 | 2,147,483,648 |
| Exact highbit lifted roots before unguessed original F1 check | 2,147,483,648 |
| Actual firstpass A6 with genuine F1 | 8,387,722 |
| Original S4 six-bit mask | 131,198 |
| Original S14 low-eight bits | 534 |
| Original S15 eighteen-bit mask | **0** |
| Original S16 additional source check | **0** |

Every index interval contains 2^27 outer domain points, and the thirty-two intervals partition 2^32 without overlap. The above values are sums of all 32 executed shard logs, not extrapolated from an incomplete pilot. The source hash and original 132 selected-withheld mask equations are independently checked by the Python wrapper on every shard. Reference tests use `random.Random((k1 <<32)|k0).getstate()`.

Reproducers: [C++17 exact complete bit-lift](../agents/agent23/k04_cpython_k2495_n2_inverse.cpp), [source-pinned Python genuine-seed and original packet SFT](../agents/agent23/k04_cpython_k2495_n2_inverse_sft.py), [manual 32-shard workflow](../.github/workflows/h17-agent23-k2495-n2-inverse.yml), [all-success historical source run](https://github.com/FlareZ123/workplace-v2/actions/runs/42307238090).

## Scope of this negative

The conclusion is **complete exclusion of genuine CPython `random.Random` seeds consisting of two 32-bit words when the authentic printer payloads are interpreted as hypothetical p951 native MT packets after exactly 2,495 previous outputs**. The exclusion is exact within these assumptions; it does not support claims about a different offset, key length, firmware, historical selected paper-copy integrity, or actual recovered coupon bits. This seed model has no independently verified historical producer identity. The selected physical K04 coupon remains unknown, K08 author's final desk phrase remains unquoted, six original REC8 slots still individually PASS, and combined original acceptance remains INCOMPLETE.

The stronger new [joint-source affine theorem](h17-k04-k2496-sixterm-joint-affine-16-keylengths-20261106.md) independently excludes 16 seed lengths at the distinct k2496 offset and should be preferred before commissioning more symbolic inversion for those already-closed source geometries.
