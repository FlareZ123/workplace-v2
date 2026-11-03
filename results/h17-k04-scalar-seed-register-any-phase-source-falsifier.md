# H-17 K04: scalar MT19937 seed initialization excluded at all source-testable native phases

**Agent 16 | 3 November 2026.** A source-only necessary-condition test in the hypothetical p951 MT19937 printer chronology. No recovered K04 value is claimed.

## New model and its boundary

Previous scalar-init studies tested specific first-output origins, selected pre-spool donor positions, 624 rotations of one register window, or several prescribed complete-twist offsets. This test allows **every possible start of an untwisted 624-word scalar-initialized register overlapping the original reconstructed native-state window**.

For native 32-bit scalar MT19937 initialization, every initialized register must obey:

    S[i] = (1812433253 * (S[i-1] XOR (S[i-1] >> 30)) + i) mod 2^32
    for i=1..623

If the register starts at native stage p, any source-fixed original consecutive pair X[t-1], X[t] inside that register must obey this equation with i=t-p. One contradictory exact pair excludes **every unsigned 32-bit seed** at that phase, independently of any seed search.

## Blind original-source data and executed count

Original printer source SHA256: **7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083**. The source model is the existing [Agent49 exact p951 symbolic basis](../agents/agent49/k04_p951_symbolic_basis.py). The 18:02 disputed selected ACK row129 is excluded before fitting. All **132 other original packets** produce rank **15,365** and completely determine **991 native 32-bit words** across stages -1100..+1040.

For every candidate initialized-register start **p=-1722..+1040 inclusive**, enumerate its usable consecutive original fully source-fixed native word pairs and test the exact scalar recurrence. The original selected ACK bytes, XOR mask, K04 commitment, K08 nonce, candidate and verifier were never read by the test.

| Window | Candidate phases | Contradicted by exact original pair | No fully fixed adjacent pair |
| --- | ---: | ---: | ---: |
| All starts overlapping the observed native window | **2,763** | **2,732** | **31** |
| Starts satisfying p+624 <= 0, able to precede printer row0 | **1,099** | **1,080** | **19** |
| Complete initialized-register windows wholly within -1100..1040 | **1,518** | **1,518** | **0** |

All 2,732 testable starts were rejected, with **zero** original-source matching complete scalar-init adjacent transitions anywhere in this fixed model. The 31 untestable boundary starts are exactly **-1722..-1704** and **+1029..+1040**. No contradiction can legitimately be asserted for a window without a full original pair.

Five source witnesses for independent reconstruction:

| Candidate phase p | Source-fixed adjacent pairs | First contradictory pair at t | Predicted X[t] | Actual original X[t] |
| ---: | ---: | ---: | ---: | ---: |
| -1703 | 1 | -1080 | 753572125 | 1337010897 |
| -1100 | 98 | -1080 | 753571522 | 1337010897 |
| -900 | 126 | -851 | 771266519 | 2761593218 |
| -800 | 135 | -791 | 414196939 | 712121479 |
| -624 | 131 | -621 | 1340366375 | 827516875 |

All differences are exact 32-bit integer inequalities.

## Real seeded, sparse-source controls

The [single-file reproducer](../agents/agent16/k04_scalar_seed_any_phase_sft.py) generates genuine scalar MT19937 initialized states, standard twists, and printer observations at the same 132 intact packet positions as the original. It hides synthetic row129 before rebuilding the source basis.

- Seed 5489, true initialized register at phase -1100: **98/98** source-fixed adjacent initialization transitions agree.
- Seed 0xDEADBEEF, true initialized register at phase -800: **135/135** agree.
- Three additional fully known scalar-initialization controls at phases -1100, -777 and -497 agree on **623/623** transitions each.
- Independent reference calculation from seed 5489 produces first tempered MT output **3499211612**.

Reproduce at repo root with Python standard library:

    python agents/agent16/k04_scalar_seed_any_phase_sft.py

Existing Agent49 source helper pins the original printer SHA256 and omits disputed row129. The SFT is read-only, with extensive count assertions and independent positive cases.

## Precise implication and remaining work

**This is a complete source-conditioned exclusion for all 2,732 testable native seed starts in the stated window.** It broadens specific rotation/origin exclusions, without implying that the p951 producer is historically authenticated.

A scalar initializer at a **much earlier epoch** whose entire untwisted 624-word register lies outside the recoverable state horizon is not tested. Those additional unknown initial draws, alternate chronology, CPython multiword seed initialization, independent or reseeded writers, and selected physical-media corruption remain possible. Even the 19 left-boundary forward-start possibilities have no source-fixed adjacent pair and cannot be excluded by this test. Other generator families are outside its scope.

**No historical selected coupon bit is newly authenticated**, and no exact K08 final-caption wording was found. K01/K02/K03/K05/K06/K07 remain individually PASS; K04/K08 MISSING; REC8 combined INCOMPLETE. Further progress needs a source-indexed target-reaching producer or original physical coupon/copy witness, or an author-final keeper-caption text.
