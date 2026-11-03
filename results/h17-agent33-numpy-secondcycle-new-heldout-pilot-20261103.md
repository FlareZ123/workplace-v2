# Agent33: NumPy MT19937 second-cycle SeedSequence pool4 pilot (3 November 2026)

**New source-only producer-class tests; original REC8 remains 6/8. No source-authenticated selected K04 coupon bit or K08 author-final word.**

## Distinct generation hypothesis

Earlier original-source work excluded 620 NumPy `SeedSequence` four-word-pool *first-cycle* phases. A different source model places intact original printer pairs 227 words apart in the **second** MT19937 cycle, after a complete in-place initial twist. This is historically unverified: the original print host has no source-attested NumPy implementation or phase.

Five original untempered 227-apart pairs (previously derived from 132 source-valid print rows with selected row129 excluded) determine four contiguous native previous-cycle words `6CE0E225 F4E8FCB2 C517EB25 7D3AAF35`. For each source phase p, form exact 32bit `SeedSequence` pool equations for first twist T, second twist U, and assert all ten observed 32bit U pair values at indices p..p+4 and p+227..p+231. For p at least 21, also assert the **twelve independently intact original 07:00, 07:05 and 07:10 printer words** at offsets p-21..p-18, p-14..p-11 and p-5..p-2. Earlier p include only stage-reachable controls, not fictional negative indices.

The original printer input has SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. No selected ACK payload, K04 mask/hash, K08 nonce/commitment or candidate is fitted or tested in this pilot.

## Completed decisions with bounded Z3 QF_BV

- **Phases 0..70 inclusive:** 71 tested using 2.4/2.5-second SMT limits and a separate 7-second hard process limit. **23 definitively UNSAT** phases: `0,2,4,5,9,10,11,13,15,16,20,25,30,39,40,42,44,48,50,54,61,67,68`. The remaining **48 returned UNKNOWN**, not an exclusion; zero SAT.
- **Phases 180..209:** thirty tested at 1.5-second SMT limit, **all UNKNOWN**, zero SAT or UNSAT.
- A weaker source-pair-only initial pilot yielded definite UNSAT decisions in other original phases but was superseded for this report by the better heldout-record model.
- **Positive structural controls:** genuine NumPy MT19937 outputs with independent seeds `1234,17,5` at test phases `0,13,99,218,390`, with all reachable independent early-row controls and ten paired outputs, return **SAT in all five cases** when their authentic four-word generated entropy pools are pinned as fixed test witnesses. This proves the SMT formula allows five actual planted producer histories, though it does **not** validate free-pool search convergence. Previous first-twist output controls are likewise established in Agent28's secondcycle SFT.

The Z3 backend was the installed `libz3.so.4` accessed using its SMTLIB2 evaluation interface. Return statuses were distinguished directly. The original 48+30 UNKNOWN phases may contain a valid pool, or simply require a stronger solver/time budget. No SAT witness from real original data, no predicted selected coupon, no verified K04 component.

## Research consequence

This closes 23 original-source phase assignments under a new secondcycle constrained producer family, but leaves the overwhelming portion of the model unresolved. Do not promote solver UNKNOWN to producer exclusion or proof of irrecoverability. Given the historically unproven NumPy origin, actual future-stage original coupon witnesses still have much higher target value. Prior source work: [Agent33 firstcycle](h17-k04-numpy-seedsequence-full-pool-firstcycle-exclusion.md), [Agent17 firstcycle boundary](h17-k04-numpy-pool4-boundary-227-phase-exclusion.md), and [Agent28 independent secondcycle solver](../agents/agent28/k04_numpy_pool4_secondcycle_sft.py).

K01/K02/K03/K05/K06/K07 remain individually PASS; K04/K08 MISSING, REC8 combined INCOMPLETE.
