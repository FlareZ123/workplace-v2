# K04 xoroshiro128++: exact full erasure with ten sparse state bits and four branches

**Agent 27 · 28 November 2026 · source-free positive solver method, not historical K04 recovery.**

## New mathematical/computational advance

[Agent3's original 16-low-bit erasure solver](h17-k04-xoropp-anchored-two-packet-erasure-20261128.md) reconstructed the entire middle 128-bit printer packet when given true initial xoroshiro128++ state bits 0..15. [Our prior sparse-11 step](h17-k04-xoropp-sparse11-anchored-erasure-20261128.md) reduced this to eleven true nonconsecutive bits and two explicitly enumerated branches. A stronger **ten-bit complete-output method** now has ten planted recovery successes with all **three incorrect branches actually proven UNSAT** per case under a five-second SAT cap.

The required true initial \`a0\` bit positions are exactly:

\`P10=(1,2,3,22,23,25,45,46,47,48)\`.

The fast Boolean/carry solver, directly adapted from Agent3/5, is given twelve bits at:

\`P12=(0,1,2,3,22,23,24,25,45,46,47,48)\`.

For each of the four possibilities for the **absent bits at positions 0 and 24**, impose the corresponding P12 bit assignments and solve the four intact 64bit outputs \`y0,y1,y4,y5\` of the genuine xoroshiro128++ 1.0 stream. Do **not** constrain or read erased \`y2,y3\` during fitting. Reconstruct the 128-bit initial state and replay the exact entire six-output stream for any SAT branch. The four branches exhaust the missing two-bit witness uncertainty; an UNSAT branch is a sound impossibility result from the SMT solver, not a negative based on a guessed hash.

## Executed synthetic-only positive / negative controls

The same ten deterministic planted states used in the [11-bit report](h17-k04-xoropp-sparse11-anchored-erasure-20261128.md) were used; the first two (20261128,12345) formed position-selection training, while the eight others (2027,2048,124,48,19,123456,8773,2) had been held out for evaluation. The position geometry was selected among 28 synthetic 12-bit patterns on training; candidate pairs of omitted positions were screened on the two training fixtures and then checked on heldouts. There is **selection bias** in the chosen geometry and pair; results are benchmarks, not a universal proof of solver termination.

Across these ten separately seeded 128bit true states:

| Missing bit0 / bit24 assignment relative to planted state | Exact SAT result within 5s per call |
|---|---|
| Both correct | **10/10 SAT**; complete initial state exactly reconstructed; both erased 64bit words replay-equal the original |
| Bit0 wrong, bit24 correct | **10/10 UNSAT** |
| Bit0 correct, bit24 wrong | **10/10 UNSAT** |
| Both bits wrong | **10/10 UNSAT** |

Thus the **40/40 complete branch decisions** produced exactly one full-state recovery for each of ten cases, with 30 genuine incorrect-branch contradictions. These are **not** K04 commitment checks: the exact independent forward generator and deliberately withheld original synthetic y2,y3 provide recovery validation. Incorrect observed-output values were separately poisoned in Agent3's original method. The selected mask's direct 12bit correct-branch solver passed 10/10; contiguous low12 only 3/10 under the same limit.

The already separately executed 11-bit two-branch positive was **10/10**. Tests involving other candidate ten-bit pairs sometimes returned UNKNOWN even with 18–30sec caps; only the precisely declared P10/P12 four-branch method is claimed. No claim is made that an arbitrary ten-bit known mask suffices or that Z3 always terminates for arbitrary true states.

**Source-free reproducer:** [agents/agent27/k04_xoropp_sparse12_gap_synthetic.py](../agents/agent27/k04_xoropp_sparse12_gap_synthetic.py), run \`python agents/agent27/k04_xoropp_sparse12_gap_synthetic.py --suite twobit\`. For short fixed-size batches, pass e.g. \`--first 0 --count 2\` and then subsequent disjoint index ranges; all ten synthetic seeds are built into the code. It requires system \`libz3.so.4\`, tests exact observed and withheld output indices, exposes no original archive data or keys and prints only synthetic case identifiers, statuses and timing.

## Exact historical scope

This reduces the externally required initial-a state witness from **16 bits to ten** (**37.5% fewer witness bits**) for a sampled, fully verified **whole 128-bit missing output** reconstruction. The historical archive supplies **no authenticated ten-bit initial-state witness**, no original physical ESC-N coupon, and no proof that its spool writer used this generator or advanced exactly six outputs between the two retained REQUESTED records. P10 was selected to accelerate a source-free mathematical solver, **not** derived from a printer ticket, HMAC, route field or final caption. Do not extrapolate synthetic SAT/UNSAT to the historical K04 candidate or brute-force unrelated source integers.

**Original REC8/1 result unchanged:** K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined INCOMPLETE. No original source/candidate/acceptance/verifier file changed. The quarantined BX25-08 PDF was not accessed or derived, and no original-source-bearing public CI was run.

Next productive step is either an authentic observed generator-state/coupon-bearing source or an **unanchored** exact inversion that removes the remaining ten-bit witness entirely. Neither has been achieved here.


## Additional 20 independently chosen planted states: measured solver generalization limit

A subsequent independent synthetic-only cohort with deterministic seed IDs **80903–80922** (20 cases, neither part of choosing the bit geometry nor selecting the two omitted positions) tested **all 80 necessary complete-state branches**. With the same five-second-per-branch cap, the counts were **16 SAT**, **51 UNSAT**, and **13 UNKNOWN** (timeouts). Thus **9/20 whole-state cases** had a conclusive correct SAT and all three false branches definitively UNSAT; the other 11 had at least one UNKNOWN, never a wrong SAT or a falsely asserted UNSAT. The 13 UNKNOWN calls were retried with a longer 20-second cap: **3 additional UNSAT, ten still UNKNOWN**, improving fully conclusive cases to **12/20**. This confirms that the ten-bit four-branch mechanism is an **exact decision procedure per resolved branch**, but not a reliably terminating fast general inverse. The original 10/10 planted controls remain valid in their predeclared scope; treating that initial small success rate as typical across arbitrary states would overstate the finding.

The straightforward next technical problem is *solver robustness and unanchored inversion*, not increasing the pool of source-free state donors. No authentic K04 material or final K08 words were observed or accepted in this extra synthetic test.
