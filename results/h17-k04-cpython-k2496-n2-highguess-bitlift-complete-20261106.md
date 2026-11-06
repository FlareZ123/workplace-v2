# Exact genuine CPython n2 source inversion at k2496: UNSAT by complete bit lifting

**Agent 4 | 6 November 2026 | exhaustive original-source *conditional* exclusion.** This is a different, successful computational method from Agent17's 1,200-second Bitwuzla `UNKNOWN` for genuine CPython two-word integer seeds. It does **not** recover K04's physical 18:02 coupon or K08's verbatim final caption. Official REC8/1 remains six individual PASS, K04/K08 MISSING, combined INCOMPLETE.

## Original source observations and conditional scope

The input is the **132 intact original spool packets with the disputed selected 18:02 ACK2 packet (row129) withheld**. The p951 MT19937 four-native-word printer chronology is an **unproven hypothetical producer**. The source-only initialized-register projection was independently assembled by Agent28 and Agent17 and has rank 15,365 and 711 fixed initialized bits at genuine CPython output startup offset **2496**. The original spool SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

This exact inversion uses only these necessary original-source observations; they are included in the previously published Agent17 [bidirectional source inversion](h17-k04-cpython-k2496-bidirectional-shortstate-inversion-20261106.md).

| Initialized register | Mask | Source value |
| --- | --- | --- |
| S2 | `09CC1C00` | `00C40000` |
| S5 | `8000001F` | `00000011` |
| S6 | `FFFFFFFF` | `E403BB7D` |
| S7 | `FFFFFFFF` | `1F7B301F` |
| S8 | `09CC1C00` | `008C1000` |
| S15 | `000000FF` | `000000B6` |
| S16 | `5398BA7D` | `4010A820` |
| S17 | `01800800` | `00000800` |

The 32-bit first-pass seeded array is `Ai=(Gi XOR F1(A(i-1)))+k[(i-1) mod2]+[(i-1) mod2]`, where `G0=19650218`, `Gi=1812433253*(G(i-1) XOR (G(i-1)>>30))+i`, and `F1(x)=1664525*(x XOR (x>>30))`. In the second pass, `Si=(Ai XOR F2(S(i-1)))-i` with `F2(x)=1566083941*(x XOR (x>>30))`; operations are unsigned modulo 2^32. For i=3..17 the predecessor relations do **not** depend on CPython's wrapped S1 history.

Original source S6/S7 exactly fixes

```text
A7 = (S7 + 7) XOR F2(S6) = 2AED5290
```

and original S8 is independently a **k1-only** masked condition (Agent27's support analysis). General-purpose nonlinear 17-step bit-vector inversion remained `UNKNOWN` on both n2/n3 in Bitwuzla after 1,200 seconds. The exact finite inversion below resolves **n2**.

## Exhaustive 2-adic algorithm

For each actual full 64-bit integer seed split into two unconstrained 32-bit words `k0,k1` (including `k1=0`, so the search is conservative), there is precisely one choice of each unknown high-two-bit state register. Enumerate all **4^6=4,096 high-two-bit patterns** for first-pass A1..A6 and all **4** high-two-bit S5 guesses. Given any such fixed high bits, `x XOR (x>>30)` is **triangular from the least significant bit upward**. At each of the 32 bit positions, recursively try all **four** new `(k0_bit,k1_bit)` assignments and discard a partial assignment only after the following *necessary* original-prefix constraints fail:

1. firstpass A7 low bits equal the corresponding original fully known A7 bits;
2. the full original S7→S8 expression matches every currently available `S8 & 09CC1C00` source bit;
3. reverse from original S6 to S5 via `S5 = (0x6A76AE6D * (A6 XOR (S6+6))) XOR high2(S5)`, imposing all available `S5 & 8000001F` source bits;
4. once bit10 is reached, enumerate all **4^3=64** high-two-bit choices for intermediate S4/S3/S2 and reverse sequentially `S5→S4→S3→S2`, imposing the available `S2 & 09CC1C00` bits. Bit10 is the lowest fixed S2 position, so delaying these 64 choices does not discard any source-fitting seed;
5. when bit30 and bit31 are assigned, explicitly verify **every guessed first-pass and second-pass high-bit pattern** against the actual completed words.

At completed key words, evaluate actual first-pass A8..A17 (without guessing high bits) and genuine local second-pass S7..S17 from source-fixed S6. Filter original S15, S16, S17 masks. There is no heuristic, arbitrary seed size cap, key range truncation, dropped branch, omitted high-bit choice, original selected-copy constraint, K04 commitment test, or model-implied physical bit claim. Every original-compatible genuine CPython n2 seed must survive one branch in this finite search.

## Actual complete original-domain result

Run the pinned standalone [C++17 exact n2 bitlift SFT](../agents/agent4/k04_cpython_k2496_n2_highguess_bitlift_sft.cpp) with high-guess start **0** and count **4096**; its arguments also support disjoint exact geometry shards. The validated source is 8,394 bytes, UTF8 SHA256 `785505465d9ebe6d677e3e2910e9fa799c1260b1b66b81f3785b9978466c1cd6`, Git blob SHA `0e1d22c06a500b6564ce4dd5b2304814933d1f21`.

```text
INDEPENDENT_CPYTHON_FIXTURE_PASS
PLANTED_FULL32_DFS_PASS k0=12345678 k1=23456789 ha=2904 s5hi=1 s234hi=55 nodes=112929 planted=1
PLANTED_FULL32_DFS_PASS k0=1fc3 k1=1092 ha=2219 s5hi=1 s234hi=7 nodes=45525 planted=1
PLANTED_FULL32_DFS_PASS k0=ffffffff k1=ffffffff ha=3851 s5hi=3 s234hi=23 nodes=127973 planted=1
PLANTED_FULL32_DFS_PASS k0=0 k1=80000000 ha=2099 s5hi=2 s234hi=58 nodes=62413 planted=1
K2496_N2_HIGUESS start=0 count=4096 visited=1334836524 bit10=524288 bit29=67468816 leaves=253 s15=1 s16=0 s17=0 roots=0 seconds=42.2547
```

The exhaustive original run finished in **42.25 seconds** with `g++ -O3 -std=c++17` on a local CPU. Its search-level counts include 1,334,836,524 retained prefix nodes, 2,148 prefix pairs that passed the preliminary bit31 stage, 253 complete root states after the final high-bit consistency check, **one** surviving original S15 observation, and **zero** surviving original S16 observations. Thus **no two-word CPython integer seed survives even these eight necessary source observations**.

The four genuine seeded planted controls each compute a complete 624-word CPython initializer and then recover their exact original k0/k1 through the full recursive search, under source masks synthetically derived from their own genuine full initialized registers. In addition, the SFT asserts **nine independently computed actual Python `random.Random((k1<<32)|k0).getstate()` reference words**, including indices100 and623, for the seed `(0x12345678,0x23456789)`. The correctness of 624-firstpass wrap handling is thus independently controlled. The original source is never modified.

## Relevance and limit

This is the first completed **n2** source exclusion at the previously open k2496 true CPython output startup and one of the few exact results that **improves on a real solver `UNKNOWN`** without pretending a timeout proves UNSAT. Together with Agent47's completed n1 k2496 search, the same speculative k2496/p951 printer producer now has n1 and n2 integer-seed classes excluded; **n3/n4 and other issuer families remain open**. Separately, Agent23 completed n2 k2492/k2493, and Agent4 has a distinct completed n2 k2494 inversion.

**No actual physical coupon, terminal author-final wording, K04 selected bit, or new accepted component was recovered.** This mathematical exclusion is conditional on the exact hypothetical p951 printer stage chronology and genuine CPython integer seeding, neither independently proven historical. The next high-information target is an independently authenticated 18:02 printer producer/copy-stage witness or Emily's actual final text/version, rather than launching arbitrary adjacent-offset or phrase-volume sweeps.
