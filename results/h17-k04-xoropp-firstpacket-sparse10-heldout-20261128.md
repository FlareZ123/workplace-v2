# K04: ten-bit xoroshiro128++ erasure solver now fits only first intact packet and predicts independent second packet

**Agent 27 · 28 November 2026 · new full-output synthetic mechanism and independent holdout; historical physical K04 not recovered.**

## Important change from the previous ten-bit model

The [preceding sparse ten-bit solver](h17-k04-xoropp-sparse10-four-branch-erasure-20261128.md) fit **both** intact hypothetical outer printer packet pairs \`y0,y1,y4,y5\`, withholding only the erased middle pair \`y2,y3\`. It reconstructed the whole planted state in 10/10 selected fixtures, but the 20 subsequently unseen seeded states yielded only 9/20 complete SAT/UNSAT decisions within five seconds per branch, 12/20 after extending unresolved branches to20 seconds.

This stronger revision **removes y4 and y5 entirely from the SAT circuit**. It fits only the first two consecutive 64bit outputs \`y0,y1\` (hypothetical 18:01 REQUESTED attempt1); the entire middle \`y2,y3\` and the later pair \`y4,y5\` (hypothetical 18:03 REQUESTED attempt3) are **never given to the solver**. The recovered 128bit state is then independently replayed to predict **all four later 64bit words**, so both the missing packet and the second intact packet are legitimate full-object holdouts. This is a causally stronger benchmark, not just a rehash of a 256bit fit.

## Exact finite construction

Fix just **ten actual initial-a state bits**, selected by an earlier source-free geometry search:

\`P10=(1,2,3,22,23,25,45,46,47,48)\`.

Using the output-conditioned 64-variable Boolean carry circuit inherited from [Agent3](h17-k04-xoropp-anchored-two-packet-erasure-20261128.md) and Agent5, enumerate the four possibilities for **two unknown bits (0 and 24)** to reach the fast twelve-bit mask:

\`P12=(0,1,2,3,22,23,24,25,45,46,47,48)\`.

For each of four branches, solve exactly **only** the two 64bit output equations \`y0,y1\`. For each SAT state, forward-generate the original six-output xoroshiro128++ 1.0 stream and independently verify the withheld outputs \`y2,y3,y4,y5\` against the synthetic ground truth. Check false branches with exact UNSAT; UNKNOWN remains inconclusive rather than a rejection.

This still needs an **unavailable ten-bit true state witness** and a **historically unproven xoroshiro++ producer**. Nothing about original K04 bytes or source physical copy is assumed during solving.

## Original-free planted controls and broad heldout test

| Cohort / problem | Complete four-branch cases at 5 s/call | Correct-state SAT | Wrong-branch UNSAT | UNKNOWN |
|---|---:|---:|---:|---:|
| Ten previously studied seeded states (2 train, 8 heldout) | **10/10** | **10/10** | **30/30** | 0 |
| **Twenty new independent seeded states** (IDs80903..80922) | **19/20** | **20/20** | **59/60** | 1 |
| **Total first-packet-only** | **29/30** | **30/30** | **89/90** | 1 |

All **30 recovered states** reproduced the original entire six-output planted generator stream exactly, including the 128-bit missing middle pair and the 128bit later pair **that was not part of the SAT constraints**. The one inconclusive false branch is a time-limited UNKNOWN on fresh seed80905, not a reported SAT or UNSAT. There are zero wrong SAT states. Each branch used the same fixed five-second Z3 cap on the same local host; speed is hardware/solver dependent. The twenty fresh states were **not** used in choosing the witness geometry/omitted bits. The original ten were training/earlier holdout for geometry selection; do not pretend all 30 were prespecified independent parameter-selection holdouts.

The previous both-packet-fitting approach on those same fresh20 had **9/20** complete under5 seconds, versus this first-packet-only method's **19/20**, despite fitting *fewer* observed outputs. Removing later full-output constraints from the SAT search substantially helps search and creates an actual later-packet causal holdout. The result is a marked solver robustness advance over the earlier dual-flank model, not a guaranteed uniform-state polynomial inverse.

## Reproduction and strict scope

[Single synthetic-only exact solver](../agents/agent27/k04_xoropp_sparse12_gap_synthetic.py) now implements both modes. With system \`libz3.so.4\`, run:

\`\`\`sh
python agents/agent27/k04_xoropp_sparse12_gap_synthetic.py --suite firstpairtwobit
python agents/agent27/k04_xoropp_sparse12_gap_synthetic.py --suite firstpairtwobit --fresh20 --first 0 --count 20
\`\`\`

The second command accepts an inconclusive timeout and reports aggregates without claiming UNSAT for UNKNOWN; on short runtimes split the disjoint fresh indices using \`--first\` and \`--count\`. No original bytes, target hash, mask, K08 wording or PDF are loaded or printed. The scientific result is strictly a *synthetic generator-state reconstruction method*. It may be used against actual intact 18:01/18:03 REQUESTED records **only after** an independently justified producer/state bridge, correct serialization and assumption of exactly two lost intermediate outputs. The original physical RECOVER ACK2 coupon remains unobserved and the original K04 commitment has **not** been met.

The key acceptance remains **K01,K02,K03,K05,K06,K07 PASS; K04,K08 MISSING; combined REC8/1 INCOMPLETE**. Official evidence, acceptance, verifier and canonical candidate unchanged. Quarantined BX25-08 PDF not read/derived; no original-bearing public CI executed.

**Actual next frontier:** remove or derive the ten state bits from recorded source, or develop an efficient unconditional inverse from only y0,y1 with second packet y4,y5 genuinely held out. Publishing more guessed ten-bit donors without producer linkage will not authenticate K04.
