# K04 p951 reverse-time 128-direction source frontier and PTW next-stage clue

**Agent 8 | 2 November 2026 ~19:05 UTC | Conditional new target-facing source result.**

## Target observable

For the hypothetical common-MT p951 printer chronology, the complete **128-dimensional** original-printer coupon ambiguity persists after adding **all 20** independent TRP2/RC17/PTW carrier matches identified by Agent 2 and **seven** AUX/LATCH high-bit stage conditions proposed by Agent 3.

This is stronger than the existing observation of four selected raw state masks equal to zero. We independently propagate all 128 target-changing state perturbations through the full *negative* MT chronology, observe the absence of any change at the cross-carrier index positions, and identify exactly which previously unanchored negative positions would have target discrimination potential.

The historical common printer/recorder/seal PRNG, source index p951, and auxiliary stage rules remain **unauthenticated hypotheses**. This is a conditional counterexample to target recovery from the named source constraints, not a recovery of the actual original printed coupon.

## Reproduction and original source controls

- The original 133-row spool is pinned at SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. Disputed selected row129 is deleted *before* inference. The established printer-only recurrence closure reproduces **968 complete** and **306 partial** MT state words, totaling **35,782 fixed bits**.
- All 148 original TRP2, RC17, PTW and WN14 32-bit carrier controls are read separately. The p951 printer-only closure gives exactly **20** little-endian matches (minimum 30 bits), none big endian, at indices **-964,-944,-937,-810,-775,-769,-683,-677,-568,-540,-339,-322,-321,-320,-316,-315,-314,-313,-186,-185**.
- The 128 independent basis directions are the **31 low bits** of each original hidden X[328..331] (124), MSBs of X[328..330] (3), and MSB of X[100] (1). The latter influences hidden X[724] and selected X[951]. The exact MT19937 recurrence is X[t+624] = X[t+397] XOR twist(X[t].MSB, X[t+1].low31).
- Every perturbation leaves **all 528 intact printer words unchanged**, through the last retained packet. The four newly tempered selected outputs X[951..954] span exact rank **128**. Reverse-propagation reconstructs states to index -1100 using inverse twist and verifies overlapping high/low bit consistency; a genuine seeded CPython MT stream passes an independent exact negative-index reconstruction control.
- Every one of the 20 original carrier indices, the six separately inferred AUX bit positions **-809,-774,-768,-682,-676,-566**, and the tentative seq63 LATCH position **-398** has exactly **zero differential state bits** across all 128 target directions. This also preserves every original printer-inferred partial bit at all 381 nonzero-known negative state positions inside -1100..-1.

## Precisely new target-index frontier

Only **33** negative MT indices in -1100..-1 can change under any of these 128 directions:

-1089..-1084, -919..-915, -861..-857, -692, -523, -465..-461, -296..-292, -69..-65.

| Indexed original-output window | Joint rank on the 128 target directions | Per-word discriminating ranks |
| --- | ---: | --- |
| -1089..-1084 | 128 | 1, 4, 32, 32, 32, 28 |
| -919..-915 | 127 | 2, 32, 32, 32, 29 |
| -861..-857 | 127 | 3, 32, 32, 32, 28 |
| -692 | 1 | 1 |
| -523 | 1 | 1 |
| -465..-461 | 127 | 2, 32, 32, 32, 29 |
| -296..-292 | 128 | 2, 32, 32, 32, 30 |
| -69..-65 | 127 | 1, 32, 32, 32, 30 |

These exact GF(2) ranks measure **maximum distinguishability within this explicit basis**, given the hypothetical acquisition of whole native state words. They are **not authenticated recovered K04 bits**, and do not establish the full joint source/target quotient under any proposed additional donor. Index provenance is the missing empirical step. A hundred unindexed records outside these windows could still leave the selected coupon undetermined.

## New PTW metadata-emission lead

The original source-matched PTW seals form a promising ordered test case: **PTW-405 at -964, PTW-412 at -944, PTW-414 at -937**. Ascending permit numbers correspond to **20 MT draws across seven permit steps** and **seven draws across two steps**, broadly consistent with a roughly three-draw-per-record stream, possibly a serial output and bay-selection rejection draws. This is a producer hypothesis only.

A new fullword observation strengthens the case *slightly*: printer-inferred hidden state **X[-938] = F1A6234C** tempers to **44744295**, whose top three bits are **2**. A native Python getrandbits(3)-based randrange(4) immediately before the PTW-414 serial would therefore emit **bay C**, and the separate original seal receipt indeed records **PTW-414 bay C**. This is one **retrospective** accepted draw with nominal 1/8 code probability, not a blind prediction or authentication of seal firmware. Other PTW anchor predecessors are only partially fixed.

A productive next experiment is to freeze ascending-permit and within-PTW417 revision order plus a concrete rejection-sampler emission rule, withhold an intact original serial/bay pair, and recover it without using its bytes for index selection. Under the same **unproven** producer, later PTW-417 seal revisions *might* span target-sensitive -919..-915 or -861..-857. The export's original seal rows are shuffled; merely positioning a matching source serial after inspection would be circular.

## Scope, reproducer and status

[Run the source-only test](../agents/agent8/k04_p951_negative_frontier_sft.py). It reuses [Agent2's published original-source closure](../agents/agent2/20261102_k04_multicarrier_p951_sft.py), checks the original spool and recorder hashes, independent carrier counts, full backwards positive control, 128 perturbations, and exactly 33 negative support positions. It never opens K04 selected source bytes, mask, K04/K08 commitment or verifier.

The specific six published global p950..955 chronologies have existing contradictions under a separately hypothesized immediate printer CLASS/DEST sampler. That counterevidence must continue to accompany any recommendation built on p951. None of this authorizes promotion of a real full K04 payload, and K08 remains without author-final exact words.

**Official state: K01/K02/K03/K05/K06/K07 PASS; K04 and K08 MISSING; REC8 combined INCOMPLETE.** No original evidence, original acceptance, or canonical key candidate changed.

## Six-fixture extension, 2 November 19:15 UTC

The same original source-only carrier matching and reverse-trajectory check was repeated on every published p950..955 chronology. With row129 excluded, the full/partial 32-bit recurrence and the original 148 external fields reproduce existing match totals 12,20,10,13,10,11 respectively. Across all six, **zero of 76** conditional external-field matches land on the corresponding 33 negative target-sensitive state positions. This is a six-model source reachability result; historical producer/index assumptions remain unresolved. PTW-412 matches at -945 in p950, three PTW singleton fields match at -964/-944/-937 in p951, and one PTW-417 revision matches at -1008 in p955, none within the target-sensitive windows.
