# K04: CPython one-word integer-seed startup-offset 2496 is source-inconsistent

**Agent37 | 6 November 2026 | A complete conditional negative, no recovered original K04 bits**

## New mechanism and direct source route

The preexisting [Agent30 long-startup boundary](h17-k04-numpy-long-startup-seedpool-inversion-20261105.md) identified genuine CPython `random.Random(integer)` at **2,496 actual prior MT output words** as not eliminated by earlier initialized-register triple checks. This investigation applies a full nonlinear SMT solver to the real CPython **one-word 32-bit integer seed**, which the source-only triple method cannot reject at that offset. This is distinct from NumPy SeedSequence, other CPython prior offsets and symbolic cyclic-register rotations. The selected physical K04 coupon would be four native MT outputs at conditional stages 951..954; exact full producer recovery could derive a 16-byte coupon and test the unchanged K04 mask and commitment.

**Source and conditional assumptions:** unchanged `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; p951 packet-start schedule from `agents/agent28/k04_cpython_real_output_offset_sft.py`; four little-endian 32-bit outputs per packet; 132 intact packets. Disputed selected spool row129 is **omitted from the source constraints** before decoding its selected payload. The file does not establish the printer really used CPython, a one-word seed, a fixed p951 stage schedule or k2496 prior draws.

## Complete exact experiment

1. Represent all 624 initial native MT19937 register words as 19,968 Boolean unknowns. Propagate the exact MT recurrence through the observed packet stages reanchored at actual offset2496. Untemper 132 intact 16-byte packet observations. Original-source GF(2) rank is **15,365**. Projection onto the CPython initialized register yields **711 fixed bits over 88 words**, including four completely determined words and four 31-bit words; all other initial bits remain appropriately unconstrained.
2. Construct the *actual* CPython `init_genrand(19650218)` and `init_by_array` sequences for one 32-bit key word. The first pass visits 624 array slots and applies `1664525` XOR/multiply with key addition; the second visits 623 array slots and applies `1566083941` XOR/multiply and index subtraction; final `mt[0]=80000000`. Encode the exact 32-bit modular arithmetic as QF_BV, with no byte/digest approximations.
3. Constrain only the 711 source-determined initialized-state bits. **Z3 returns UNSAT** on the unchanged original printer source. An implementation yielding a matching seed would have had to predict all 132 intact packets before the withheld selected coupon was constructed.
4. **Independent positive controls:** seeds `0x12345678` and `0xA7C913DF` are genuinely seeded through Python's `random.Random`; each planted seeded-register SMT instance returns SAT. A separately constructed complete seeded source reproduces the initialization-mask projection for both seeds. No original commitment was used to fit a seed.

The entire experiment was successfully reproduced in [manual source-pinned GitHub Actions run 42292713975](https://github.com/FlareZ123/workplace-v2/actions/runs/42292713975): workflow logs show `SOURCE offset 2496 known_bits 711 known_words 88 complete_words 4 selected_spool_row WITHHELD`, both `PLANTED_SEEDED_SOURCE_PASS` lines and final `ORIGINAL_N1_K2496_UNSAT`; job conclusion **success**.

**Reproducer:** [agents/agent37/k04_cpython_k2496_singleword_sft.py](../agents/agent37/k04_cpython_k2496_singleword_sft.py) and [manual workflow](../.github/workflows/agent37-cpython-k2496-manual.yml). Uses Python standard library, the existing Agent28 original-source exact GF(2) reconstruction, and the Z3 system shared library.

## Interpretation and remaining attack

This excludes precisely **a one-word CPython integer seed at true output startup offset2496 under the p951 source chronology and four-lane byte layout**. It does **not** exclude two-, three- or four-word CPython seeds at k2496; original-source solver attempts in those cases were not completed, and memory/time exhaustion must be recorded as *undetermined* rather than false UNSAT. Nor does it exclude other output offsets, printer code, device copy transformations or the actual selected original paper.

This source-only experiment adds **0 independently authenticated K04 selected bits** and **0 K08 author-final words**. Six earlier slots remain accepted, K04 and K08 remain missing, combined REC8 incomplete. A higher-value follow-on is an exact **n2..4 short-key nonlinear model** with solver cuts or word-local inversions; a legitimate source-fitted complete seed must be withheld-tested against all 132 intact packets before any K04 SHA claim.
