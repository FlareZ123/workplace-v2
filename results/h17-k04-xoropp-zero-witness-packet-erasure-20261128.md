# K04 xoroshiro128++: executed first-packet-only zero-witness erased-packet reconstruction

**Agent 4 · 28 November 2026 · source-free mathematical recovery, not an authenticated historical K04 component.**

**Prior-art distinction:** [Agent23's 82-primary-Boolean output solver](../agents/agent23/k04_xoropp_82bool_circuit_sft.py) previously documented unanchored *four-output-fitted* synthetic SAT and an unanchored complete-model extraction path. This work does **not** claim to be the first unanchored xoroshiro128++ method. Its distinct executed advantage is a recovered full state and middle packet from **only the first intact output pair**, with the entire later packet held out for independent replay, by an explicit finite 4,096-bucket zero-source-witness search. Source authenticity remains unproven.

## Decisive new step relative to the nine-bit prerequisite

[Agent27's nine-bit conditional candidate generator](h17-k04-xoropp-ninebit-firstpacket-candidate-20261128.md) recovered entire erased two-word packets on planted controls, but required **nine genuine bits of the generator's initial state**. No historical source supplies those bits. Merely restating that obstruction cannot construct a missing component.

The new method removes the external-state-bit condition by actually enumerating **all 2^12 = 4,096 complete assignments** to the twelve sparse initial-`a` positions
`(0,1,2,3,22,23,24,25,45,46,47,48)`. These are exact disjoint partitions of the entire 64-bit initial-`a` domain, **not guesses from historical metadata**, and no branch is selected using the planted state. Each fixed 12-bit branch uses the previously validated Agent27 output-conditioned Boolean carry circuit.

For each branch, the only equations fitted are the two 64-bit outputs `y0,y1` from the first intact packet. The initial second state word is determined from `y0` and the solved first word:

`b0 = ROTR64(y0 - a0, 17) - a0 (mod 2^64)`.

Forward replay generates the *previously erased* complete two-word packet `y2,y3`; only **after** solving, the independent later two-word packet `y4,y5` is compared. A complete later-packet replay is a powerful acceptance discriminator for this particular PRNG hypothesis. It is not a certificate that a physical historical printer used this PRNG.

### Executed source-free planted proof

The first full candidate-generation run used deterministic synthetic seed **20261128**, Z3's exact Boolean carry model through `libz3.so.4`, four local workers and a **5,000 ms per-branch timeout**. No original print source, route mask, acceptance commitment, canonical candidate, desk phrase, protected PDF or derivative was accessed by the synthetic solver.

- **636 actual independently assigned branches completed** before the qualifying state was found: **482 UNSAT, 153 UNKNOWN and 1 SAT**.
- The SAT state matched the complete **128-bit planted initial state exactly**, not just the two fitted outputs.
- The reconstructed **128-bit erased middle** matched both independently generated hidden words exactly.
- The replayed **128-bit later packet** matched both withheld words exactly; neither was a fit input.
- Local wall time **646.15 seconds** for all completed branch checks, including solver timeouts. These elapsed times are environment-dependent.

**Important scope:** 153 UNKNOWN branches are *not* excluded. This is an actual zero-external-bit *candidate recovery*, **not** a proof of uniqueness or universal successful termination. Only one SAT model is requested per bucket; an alternative SAT model in the same bucket could exist. The remaining 3,460 buckets were not needed for this positive recovery and were not exhaustively adjudicated. These distinctions must survive any subsequent synthesis.

### Independent complete-state generalization (not a supplied-bit witness)

An independently seeded synthetic stream, **80904**, was then run with the same fixed twelve sparse anchor positions and *no true branch supplied* to the search. At **5,000 ms per branch** with two local workers, **292 actual branches** completed: **167 UNSAT, 124 UNKNOWN, 1 SAT**, elapsed **658.0 s**. The qualifying SAT model again reconstructed **the complete planted initial 128-bit state and both erased 64-bit outputs exactly**, followed by an exact withheld later two-word replay. This gives **2/2 independent seeded synthetic state recoveries**, not two full-domain uniqueness certificates. The increased UNKNOWN fraction illustrates solver budget sensitivity; count UNKNOWN as unresolved.

### End-to-end synthetic source-presentation controls

A second, independent integration harness generated source-shaped REQUESTED1 and REQUESTED3 packets from a planted xoroshiro128++ stream, planted a synthetic 16-byte XOR mask and corresponding SHA-256 commitment, and then *withheld* the missing packet. All four declared presentation layouts — big/little byte order, each with first/second word order — yielded **4/4 exact complete later-packet matches and 4/4 original-style commitment matches** using one planted compatible 12-bit bucket per layout. The four layouts encode the same planted stream, so they are **serialization controls, not four independent random-state solver trials**.

A second 4/4 end-to-end source-presentation control inserted **one unobserved 16-byte generator packet** between selected erased ACK2 and the later intact REQUESTED3 packet. The predictor still inferred exactly middle outputs **y2,y3** from the first packet only; it matched the later holdout at **y6,y7**, reconstructed the synthetic physical middle, and passed the synthetic original-style route XOR and SHA-256 commitment under each byte/word order. The local source runner now has an **optional, bounded 0..8 skipped-packet phase search** for the later independent holdout, with **no additional externally known state bits or SAT branches**. This is a *mechanism robustness control*, not evidence of an actual missing historical printer job.

## Reusable implementations

- [Source-free zero-witness enumerator](../agents/agent4/k04_xoropp_zero_witness_synthetic.py) consumes no H-17 material. It can execute all 4,096 state-bit partitions on any deterministic synthetic seed and print only aggregate dispositions and positive replay checks.
- [Original-source local-only interval runner](../agents/agent4/k04_xoropp_zero_witness_source_local.py) reads *only* the named PS-0417 spool text, K04 route sheet and original commitment. It is CI-denied, never scans or opens a PDF, prints only aggregate match counts, never emits the original packets, reconstructed state, selected coupon or 16-byte component, and supports disjoint `--start/--count` partition intervals. Each first-packet model is independently checked against REQUESTED3, then the predicted full middle coupon is reduced and locally compared with the unchanged K04 commitment. A nonmatching single SAT model or solver UNKNOWN does not exclude the branch.

Example source-free reproduction, from repo root with installed system `libz3.so.4`:

```bash
python agents/agent4/k04_xoropp_zero_witness_synthetic.py --seed 20261128 --workers 4 --timeout-ms 5000
```

Never run the historical source runner in public CI. A source use requires a local non-CI environment and appropriate retention/containment; no original-source execution is needed to validate the synthetic mathematics.

## Meaning for REC8/1

**This is a working source-free method for recovering a complete erased packet without a separately supplied state witness.** It does not establish the historical writer, generator phase, retry-selection relation or integrity of the printed physical coupon. A conditional REQUESTED1/ACK2/REQUESTED3 stream must reproduce the entire held-out later packet and the unchanged K04 commitment before it can produce an original candidate; any result must preserve the distinction between commitment match and authenticated historical provenance.

There is **no newly accepted original K04**, no K08 author-final text, and no combined REC8/1 PASS. K01/K02/K03/K05/K06/K07 remain the six accepted components, and K04/K08 remain unresolved. All original evidence, `resources/verify.py`, `resources/acceptance.json` and `candidate.json` were preserved.
