# K04 three-window original-carrier synthesis: 3,360 complete coupons tested

**Agent 40 | 3 November 2026 | Exploratory complete-candidate construction, zero authentic commitment hits**

## Why this test differs

Previous p951/MT19937 investigations identified native-generator state windows that, **if populated with independently known full words**, can algebraically reduce the 128-bit unknown selected printer coupon to nearly zero. Most reports stop at hypothetical donor rank, and many fit only a single carrier. This experiment actually supplies **all three donor windows with full original-source words from different record families**, constructs every resulting complete selected coupon, applies the unmodified recorded K04 XOR mask, and tests the original immutable SHA-256 acceptance commitment. It is an attempted end-to-end recovery under a speculative batch-source architecture.

The exact conditional generator is the 624-state, 32-bit MT linear source model at printer p951, derived from 132 intact printer rows, with disputed selected row129 **excluded before model building**. Its baseline affine rank is 15,365, leaving all 128 selected coupon bits free. The hypothesized *precomputed-pool/import* producer could emit several original record cohorts into separate subsequently logged batches; their recorded UTC order need not be the PRNG state-consumption order. This is a proposal, with no authenticated firmware, pool, or staging record.

## Three original-value source windows

1. **Native -919..-915:** all five original PTW-417 revision-1 seal serials, including both documented distinct Bay-A/revision-1 entries. Permute the four bay orders and the two A entries: 48 complete serial assignments. All 48 remain source-affine-compatible.
2. **Native -465..-461:** five consecutive original CRC-valid node50 TRP2 CONTROL words, in original sequence order, with sequence start 46..60. These observations are preserved outside the printer. Under a speculative CONTROL-only five-word batch (no intervening EVENT/LATCH/AUX draws), all 48 × 15 = **720** arrangements remain source-affine-compatible.
3. **Native starts -297, -296, -295 or -294:** all four CRC-valid winning node49 K05 CONTROL words seq300..303, in latch/sequence order. Among the resulting 2,880 placements, **1,980** are source-affine-compatible after all observed equations. This explicitly avoids reusing seq200/900/990's already examined negative-index lattice without a stage rationale.

The three source windows were chosen for the known conditional target quotient: a five-word -919 window, five-word -465 window, and a four-word -295..-292 winning batch can constrain the four original selected native words to **three free binary dimensions**. The concrete original source records, their sequence/bay attributes, their CRC checks, and the 132 original printer words are used as equations. The selected spool ACK2 payload is *not* used to select donor placements, fit the affine system, or make any source observation.

## Original-target result

Of 1,980 source-compatible three-window assignments, **420** have a remaining selected coupon quotient of exactly **3 bits**, all with the winning batch at -295..-292. Each thus generates exactly eight complete 16-byte coupon buffers. The exact MT temper, four little-endian words, and official K04 XOR mask produce **3,360 complete candidate component bytes**. Hashing each with the original K04 SHA-256 commitment produces **zero matches**.

There is no K04 PASS and no selected-coupon bit independently authenticated from this experiment. For the remaining 1,560 compatible arrangements with residual dimension above 15, no exhaustive target hash search was attempted. These excluded candidates were not declared impossible. Other stage placements, alternative generators, carrier byte orders, and historically different source-production processes remain outside the tested model.

**Synthetic positive control:** using a separately generated fully known 624-word initial symbolic MT state with exactly three initial-state bit variables deliberately withheld, the identical affine target enumerator recovered the correct 16-byte synthetic coupon and component from its eight possible candidates, with exactly one synthetic SHA-256 match. The original source SHA pins, recorder CRC conditions, and count assertions also passed.

Reproduce at [Agent 40 single-file test](../agents/agent40/k04_triwindow_original_sft.py). It imports the existing [exact p951 source model](../agents/agent49/k04_p951_symbolic_basis.py) and reads only original repository resources/acceptance values. Locally executed output: `synthetic withheld-3-bit coupon recovery: PASS`, then 48/720/1980/420/3360 counts, and `0/3360` original K04 commitment hits.

## What this failure changes

This construction reaches the selected 16-byte value algebraically, so its negative result rules out the **conjunction of this particular original-donor placement, explicit source values, selected-stage mapping and p951 MT model** as a complete valid K04 reconstruction. It does not show whether the p951 generator reflects historical software, whether any PTW/revision batch shares it, or whether node50 and winning node49 controls are emitted consecutively. In particular the surviving timestamps exhibit a cross-carrier generation/capture inversion: an asynchronous precomputed source would require its own provenance.

A useful next mechanism would explain **which original control emission crosses the boundary into the selected print coupon stage**, and constrain a complete candidate independently of retrospective free index selection. A novel source-specified PRNG staging/capture rule or second independent full-word donor could warrant another bounded complete-coupon construction. Growing arbitrary donor-position permutations without such a rule is much weaker.

**Official recovery state remains six individually accepted components; K04 and K08 unresolved; combined INCOMPLETE.**
