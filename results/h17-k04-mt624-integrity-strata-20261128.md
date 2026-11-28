# K04: CRC-filtered printer/recorder/seal 624-word MT reconstruction

**Agent 17 · 28 November 2026 · original-source complete-coupon test; no K04 recovery.**

## Question and distinct causal construction

Does the intact preservation export itself contain one **full MT19937 output state window** after applying the original source-quality selectors, and can that window predict the selected physical K04 coupon?

The retained sources yield a precise count: 128 ordinary first-attempt ACK printer jobs with four 32-bit words each (**512 words**), 84/88 original TRP2 recorder entries whose native CRC is valid (**84 words**), and exactly one signed, CLOSED, AS_LEFT serial for each of PTW-390 through PTW-417 (**28 words**, resolving PTW-417's multiple bay choices separately). Thus **512 + 84 + 28 = 624** words, the MT19937 state size.

The previous 624-word source-assembly screens use **different carriers and selections**: Agent 17's older 528+88+8 braided printer/recorder/K01-K06 assembly and Agent 23's 512 printer + 112 HST-4 interleave. This study does **not** re-run either construction. CRC acceptance and one-per-permit selection are source-defined, but the proposed cross-device shared PRNG, state adjacency, and permutation of three source classes are **unattested hypotheses**. The arithmetic coincidence does not authenticate producer identity.

## Exact test

Read only source-pinned, non-PDF original files and omit the disputed selected 18:02 ACK2 packet entirely. Assemble and inverse-temper 624 original observed 32-bit words with the ordinary MT19937 tempering inverse, then generate 1,024 future complete 32-bit outputs from the resulting state, checking all 1,021 possible fourword windows against the original full K04 commitment after the unchanged route-mask XOR.

The predeclared finite source-presentation family is: four PTW-417 bay selections × two recorder orders (file or timestamp) × two seal orders (permit or original record) × two printer word-byte endiannesses × two printer within-packet word orders × two recorder byte orders × two seal-byte orders × six source-group orders = **1,536** models. Test four output presentations (big/little endian, normal/reversed fourword order) per future window: **1,536 × 1,021 × 4 = 6,273,024** complete candidate checks. Also compare each generated full packet with the four untouched late printer control packets, counted as whole 16-byte equality rather than a few matching bits. No output state or 16-byte candidate is printed.

Synthetic genuine-MT generator control: reconstruct from 624 independently sampled consecutive outputs and reproduce all 1,024 withheld outputs exactly (PASS). Source pins are embedded in the executable; no original records, commitment, route, or canonical candidate were changed. Code: [integrity-strata reproducer](../agents/agent17/k04_mt624_integrity_strata_sft.py).

## Executed outcome

| Test | Exact result |
| --- | ---: |
| Structured full-state models | 1,536 |
| Whole K04 coupon component/commitment comparisons | 6,273,024 |
| Original K04 commitment matches | **0** |
| Whole original late-packet prediction matches | **0** |
| Independent genuine-MT 624-state/1,024-output positive control | **PASS** |

This closes only the specified CRC-filtered **512+84+28 full-MT-window assembly** with the declared orientations. It is not a full search of historical source order, hardware producer family, acquisition chronology, arbitrary raw-byte edit, native paper coupon, or K08 final caption; nor does it infer any authentic selected K04 bit. **K01/K02/K03/K05/K06/K07 remain PASS; K04/K08 remain MISSING; combined REC8/1 remains INCOMPLETE.**

**Next decision:** A more useful K04 attack must establish a genuine cross-record producer or physical copy-stage relation that predicts the selected *complete* 16-byte coupon, rather than simply adding other 624-word permutations after two independent 624-count constructions failed intact-output controls.
