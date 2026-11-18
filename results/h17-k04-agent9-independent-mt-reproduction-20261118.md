# K04 native MT recurrence: independent Agent 9 reproduction and source-to-target limits

**Date:** 2026-11-18  
**Author:** Agent 9  
**Status:** Independent source-signal reproduction; no K04 candidate recovered

## Question

Agent 17 reported 25 exact MT19937-style recurrence witnesses among 132 nonselected printer packets, compared with an iid 32-bit-word expectation of approximately 0.0042. The independent task was to reproduce the count without decoding the selected PS-261003-0417 ACK2 payload, challenge the iid null with packet- and metadata-preserving controls, and decide whether the signal enables a K04 source-to-target reconstruction.

## Source and exclusion discipline

- Input: `resources/evidence/print/spool-reconstruction.log` (local export path `evidence/print/spool-reconstruction.log`).
- SHA-256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- The log has 133 payload rows. Source row index 129 is metadata-checked as job `PS-261003-0417`, attempt 2, state `ACK`, class `RECOVER`, then skipped **before its PAYLOAD hex is extracted or decoded**.
- The independent implementation is `work/h17_k04_agent9_mt_reproduction.cpp`, standard C++17. It is deliberately source-specific and does not construct a K04 candidate.
- The source row order is chronological. Of 131 adjacent intervals among the 132 retained rows, 127 are 5 minutes; the four exceptions are 26, 2, 21 and 1 minute.

## Reproduction

Each retained 16-byte payload is interpreted as four little-endian uint32 words and untempered using the inverse MT19937 tempering operations. For every retained row (r), each consecutive within-row pair at positions (p,p+1) (three possible pairs) is tested. Let:

[
T(a,b)=\left(\left((a\mathbin{\&}0x80000000)\;|\;(b\mathbin{\&}0x7fffffff)\right)\!\gg1\right)
\oplus
\begin{cases}
0x9908b0df & b\mathbin{\&}1=1\\
0 & b\mathbin{\&}1=0
\end{cases}
]

A witness is a tuple (r<k<l), pair (a,b) from row (r), word (c) at any of four positions in later row (k), and word (d) at any of four positions in later row (l), satisfying (d=c\oplus T(a,b)).

For 132 rows, this geometry tests:

[
3\times4\times4\times\binom{132}{3}=17,983,680
]

possible equalities.

**Independent C++ result:** 25 unique witness tuples, exactly reproducing Agent 17's count. All 132 retained payloads are unique and all 528 untempered words are unique. The 25 witnesses involve 50 distinct source rows and 50 distinct job IDs; all participating rows are ACKs, spanning all three classes (LABEL, RECOVER, STORES) and all three destinations (bench, desk, store). Neither REQUESTED attempt participates. The 25 tuples overlap in their row references (75 row references across 50 distinct rows), so they are not 25 independent replications. Fourteen of 25 include at least one RECOVER row, but only 3 have the pair-source row `r` in RECOVER; only 5 include any RECOVER/bench row, none has RECOVER/bench as `r`, and none has all three rows in RECOVER. The signal therefore is not specifically anchored to the selected RECOVER/bench path. Re-running on the 130 ACK-only rows still gives 25 witnesses. Reversing the chronological row order gives zero.

### Witness geometry

| Row offsets ((k-r,l-r)) | Witnesses |
|---|---:|
| (52,83) | 3 |
| (53,83) | 3 |
| (53,84) | 7 |
| (53,86) | 2 |
| (54,84) | 10 |
| **Total** | **25** |

Within-row pair positions are (0,1): 15 witnesses; (1,2): 7; (2,3): 3.

The mean offsets are (k-r=53.28) and (l-r=83.92), ratio 1.575, close to the MT lag ratio (624/397=1.571). A least-squares constant row-to-output stride is 7.422 words per packet. This is suggestive of hidden output consumption between four-word packets, but it is not an alignment.

## Null challenges

The iid expectation (17,983,680/2^{32}=0.004187) is a useful reference only under independent uniform words. It is not an adequate sole null for packetized printer records.

The C++ implementation ran 96 deterministic permutations per control with `std::mt19937_64`, seed `20261118`. Each row remains a four-word packet except in Agent 17's separate flat-word control.

| Control | Mean | Median | Min–max | Trials at least 25 |
|---|---:|---:|---:|---:|
| Whole-row shuffle, all 132 | 8.06 | 8 | 2–14 | 0/96 |
| Class × destination stratified row shuffle, all 132 | 9.98 | 10 | 3–15 | 0/96 |
| Class × destination × state stratified row shuffle, all 132 | 9.82 | 10 | 4–17 | 0/96 |
| Whole-row shuffle, ACK-only 130 | 8.23 | 8 | 2–14 | 0/96 |
| Class × destination stratified row shuffle, ACK-only 130 | 9.80 | 10 | 4–19 | 0/96 |

Agent 17's flat-word fixed-multiset control (96 Python shuffles, seed 20261118) was also independently reproduced: mean 4.90625, median 5, range 1–11. The packet-preserving controls are more relevant because they retain within-packet word adjacency. None of these 96-trial controls is a calibrated p-value; they are empirical comparisons under explicit exchangeability assumptions.

## Source-to-target alignment challenge

The 25 witnesses are directionally and packet-order enriched, but do not yet identify one generator position for each packet.

- Turning every witness into the two exact MT position constraints (S_k-S_r=397+p-i) and (S_l-S_r=624+p-j) gives 50 constraints with no weighted-DSU contradictions. However, the constraint graph has 96 components, only 14 nonsingleton components, and largest component size 5. It does not connect the 132 rows into a unique global position map.
- The fitted constant stride is 7.422, but a fixed per-class/destination model assigning either 3 or 4 hidden outputs between each four-word packet (512 assignments) explains at most 4 of the 25 complete witnesses (7 first-lag and 4 second-lag matches).
- A per-row binary stride-7/8 model is infeasible, with a direct two-witness contradiction. Let each row stride be `7 + g_q`, where `g_q ∈ {0,1}` represents three or four hidden outputs after its four captured words. For witness `(r,p,k,i,l,j)`, the second MT lag requires `sum(g_q, q=r..l-1) = 624 + p - j - 7(l-r)`. Witness `(r=44,p=0,k=97,i=3,l=130,j=0)` requires `sum(g_q, q=44..129) = 22`; witness `(r=45,p=0,k=98,i=3,l=131,j=3)` requires `sum(g_q, q=45..130) = 19`. Subtracting gives `g_44 - g_130 = 3`, impossible for binary `g`. A 131-variable binary feasibility check independently returned infeasible. Thus the witnesses are not explained by a simple three-or-four-hidden-word packet-consumption schedule.

## Assessment and next step

**What is supported:** the nonselected spool records contain a reproducible, chronological-order-dependent MT-style recurrence signal. It survives removal of unacknowledged rows, packet-preserving shuffles, and class/destination/state-preserving shuffles. Duplicate payloads, duplicate words, repeated jobs, and the two REQUESTED attempts do not explain the 25 witnesses.

**What is not supported:** 25 matches do not establish a unique shared MT stream position, do not identify a seed or output-consumption schedule, and do not yield the selected K04 coupon. The row-offset ratio is suggestive, but the simple 3/4-gap packet model fails and the exact position constraints remain disconnected.

**Research-priority change:** this supports pursuing the native printer/driver framing and per-job RNG-consumption or sequence-counter metadata in the original Bundle06/native print package. It does **not** justify another generic PRNG-family sweep or a broad gap-parameter search. Until a source artifact fixes packet-to-output alignment, keep K04 unresolved and do not decode the excluded selected row as a speculative shortcut.

## Reproduction command

```bash
g++ -O3 -std=c++17 -Wall -Wextra -o h17_k04_agent9_mt_reproduction work/h17_k04_agent9_mt_reproduction.cpp
./h17_k04_agent9_mt_reproduction resources/evidence/print/spool-reconstruction.log
```

The script prints the witness tuples, source-row coverage, offset histogram, alignment checks, and all five permutation controls. It does not alter `candidate.json`, `acceptance.json`, `verify.py`, or the selected row. K04 remains unaccepted.
