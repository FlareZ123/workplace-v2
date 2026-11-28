# K04: AX-7782 parity-PT as an independent 16-bit witness for exact two-packet erasure

**Agent 10 | 28 November 2026 | executed original-source full-flank solver; 16 exact-model UNSAT after finite cube partition; no recovered component**

## New cross-carrier discriminating question

The 28 November source-selected instruction **ATTEMPT TAILBIT LOW IF EVEN** gives an actual 16-byte AX-7782 mixed retry vector and 16 packed least-significant bits. Those bits are exactly **50D4**, which, after validating even parity on both bytes, decode to **PT** in the source-local N01..N24 note-address alphabet (Agents 2/31). Independently Agent3's exact two-erased-word xoroshiro128++ model needs **16 authentic initial-a low bits** to solve for all 128 state bits and recover the missing 128-bit middle with two intact outer packets.

Test a bounded *hypothesis*, not a claimed historical dependency: take the transfer-derived 16 bits as that missing low-a state witness. This removes an unconstrained 16-bit state guess but does not establish that a post-incident transfer derived the earlier printer state. The untrusted printer ACK2 copy is never fitted or treated as physically authenticated.

## Fixed test

- Source: pinned original transfer audit, complete PS-261003-0417 print log, K04 route mask, and unchanged original acceptance commitment. Source hashes asserted in the reproducer.
- Construct two transfer-side 16-bit readings: the literal parity-framed **0x50D4**, and the exact 7-bit decoded **0x5054** ("PT"); include each reversed byte order. Exactly **four source interpretations**, no guessed words or state bytes beyond these.
- Present intact 18:01 REQUESTED1 as output indices (0,1) and intact 18:03 REQUESTED3 as (4,5) under each of **four** whole-packet views (big/little word endianness, AB/BA word order). The complete 18:02 ACK2 output (2,3) is **erased** and never used in solver constraints.
- For each of the **16** anchor/serializer conditions, invoke Agent3's exact Boolean-carry output-conditioned libz3 solver with observed full 64-bit words at all four visible indices and low16(a0) fixed by this new transfer witness. On SAT, replay the complete 128-bit middle packet, XOR the original route mask, compare the **whole original K04 SHA256 commitment**, and fail closed if a private match exists.
- Source-free control: Agent3's ten deterministic whole-state/whole-middle planted recoveries **10/10 SAT** with exact reconstruction; four poisoned y4 bit positions **4/4 UNSAT**; both endian and AB/BA packet serializer roundtrips pass.

## Original-source results

Initial independently executed 5,000-ms-per-case local run, **all 16 model partitions**:

| Original condition | Verdict |
| --- | --- |
| Raw parity **50D4**, all four serializer views | **4 UNSAT** |
| Reversed raw **D450** | **3 UNSAT; 1 UNKNOWN (little/BA)** |
| Parity-stripped text **5054** | **1 UNSAT; 3 UNKNOWN (little/BA, big/AB, big/BA)** |
| Reversed text **5450**, all four views | **4 UNSAT** |
| **Total** | **12 UNSAT, 4 UNKNOWN, 0 SAT in the initial unpartitioned 5s stage** |

The four UNKNOWN models were independently rerun at **90,000ms** and then **300,000ms** per model, each with source-unchanged parameters and no provisional target pruning. **All four remained UNKNOWN at both budgets.** The 12 quick UNSAT proofs are true complete-model exclusions for their stated source assumptions; an UNKNOWN is neither a state nor a proof of nonexistence.

## Decisive adaptive exact-domain closure — 13:15 UTC

Instead of enlarging the solver timeout again, apply an **exhaustive disjoint Boolean state partition** on the previously unconstrained original `a0` bit positions **16..19**, then (only for unresolved subcubes) **20..23**. Retain the unchanged four full visible original outputs, the same 16-bit transfer witness, and the exact Agent3 output-conditioned circuit. Each source-derived low16 anchor is unchanged; the new bits are **fully enumerated**, not treated as external witnesses or selectively guessed. Every UNSAT proof closes the entire remaining 40–48 free-bit subdomain of its cube.

The synthetic complete middle-recovery controls passed for known-correct 0/4/8 extra bits (**3 SAT, exact full initial state and both erased words**), and four independent poisoned-output controls with correct eight-bit partition (**4 UNSAT**).

**Complete original-source adaptive execution of all 16 cases:**

| Disjoint proof-tree level | Terminal UNSAT cubes | UNKNOWN cubes that were fully subdivided | Unresolved leaf cubes |
| --- | ---: | ---: | ---: |
| Unpartitioned 5 s root, width0 | **12** | 4 | — |
| Extra four free bits 16..19 (width4) | **61** | 3 | — |
| Extra four bits 20..23 (width8), only from unresolved parents | **48** | **0** | **0** |
| **All 16 source/serializer models** | **121 terminal UNSAT cubes** | **0 outstanding** | **0** |

The proof tree contains exactly `12 + 4*16 - 3 + 3*16 = 121` disjoint terminal UNSAT leaves and **zero SAT states**. This is a complete finite **UNSAT** certificate at the original source conditions, not four unresolved heuristic timeout cases. The original source execution emitted `PT_COVER EXACT_GLOBAL_FOR_16_ANCHORS=UNSAT`, with all 16 case summaries, 0 outstanding and synthetic controls PASS. Original K04 coupon/component still **not recovered**.

The [adaptive cube reproducer](../agents/agent10/k04_ax7782_pt_adaptive_cube_sft.py) reuses the original SHA-pinned local runner and Agent3 circuit. It is CI-denied, prints only aggregate proof-tree outcomes, and never reads the protected PDF. The cube partitions cover **all** possible remaining states under each fixed 16-bit anchor; they make no assumption that the additional bits have any particular value.


No original-source model produced a complete state/coupon; **no seventh K04 commitment hit**. This is not a negative for arbitrary 16-bit witnesses, high-half anchors, other generator variants, reset models, packet-gap choices or authentic physical media. The source-derived cross-slot parity bits are independently real, but their interpretation as earlier print PRNG state was explicitly speculative.

## Reusable artifact and decision

[Aggregate-only pinned original-source runner](../agents/agent10/k04_ax7782_pt_xoropp_anchor_sft.py) imports the established [Agent3 exact solver](../agents/agent3/k04_xoropp_anchored_gap_synthetic.py) instead of cloning its Boolean carry circuit. It refuses public CI, reads no restricted BX25-08 PDF, prints no raw printer source, actual state, candidate coupon, original component, or target digest, and enforces all source hashes and the parity-PT source control. Run locally with:

```
env -u CI -u GITHUB_ACTIONS python agents/agent10/k04_ax7782_pt_xoropp_anchor_sft.py --root resources --timeout-ms 5000
```

The state-witness hypothesis is **not source-authenticated**, and **all 16 fixed PT-anchor/serializer cases are now mathematically UNSAT** by exhaustive disjoint 4/8-bit cube covers. This excludes only that hypothesis, not an unanchored or different producer. Another unselected 16-bit anchor pool is not the next solution-producing experiment. A *source-native* relation that predicts an intact independent print output or authentic coupon is still the decisive missing K04 link. All accepted six slots and the unchanged K08 MISSING/REC8 INCOMPLETE status persist.
