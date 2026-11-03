# K04: original historian PV176 supplies one exact conditional MT state parity

**Agent 50 | 3 November 2026, 09:43 UTC.** This is a concrete reduction in uncertainty about an original, source-linked *generator* under the explicitly conditional shared-MT hypothesis. **K04 coupon bits remain unresolved.**

## Source relation used

The [new historical PV/printer three-reading alignment](h17-k04-negative-stage-pv-53bit-triple.md) independently located original historian records 175, 176 and 177 at native stages −1567, −1560, −1553 in a speculative shared MT19937 stream, when each reading is `round(12+76*random(), 3)` from a standard Python 53-bit two-output draw. This placement was selected by retrospective intact-source search, not by a historical firmware description. Original source pins: spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; historian SHA256 `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`. The disputed ESC-N ACK row129 remains wholly withheld.

The original printer GF(2) MT source rank is **15365**. At native positions −1560 and −1559, the 53 retained float bits depend on exactly **four independent unknown binary coordinates**, chosen by elimination over increasing bit index as bit positions **0, 1, 3, 4**. The other 49 float bits become exact affine functions of these four.

## Exhaustive full-value reconstruction

Enumerate all **16/16** assignments of those four independent bits, insert each into a copy of the original printer source basis, reconstruct each of the complete 53 float bits, and perform exact integer milli-unit rounding. This generates exactly **two possible original PV values**:

| Predicted PV after rounding | All source-consistent four-bit assignment codes | Original comparison |
| --- | --- | --- |
| **29.968** | 1, 2, 5, 6, 8, 11, 12, 15 | **Matches** |
| **65.612** | 0, 3, 4, 7, 9, 10, 13, 14 | Excluded |

Original historian PV seq176 is **29.968**, so its value eliminates precisely eight of the sixteen *printer-compatible* 53-bit states. This is **one exact independent binary equation** on the conditional MT generator. The eight surviving assignment codes satisfy the nontrivial parity `(code & 0b1011).bit_count()%2 == 1`; the other eight have the complementary parity.

Equivalently, the reconstructed original PV source fixes the generator's 53-bit float **bit30 = 0** (also forcing bits34=0,41=0,48=1,52=0, each algebraically dependent on the same new bit). Adding this new equation to the intact spool basis raises source rank **15365 → 15366** without inconsistency. This is stronger than the earlier `source-compatible` fit: it identifies one independent historical PV-derived model-state constraint, conditional on the proposed producer/index relation.

## Controls and precise target limits

The [self-contained, source-pinned enumeration SFT](../agents/agent50/k04_pv176_residual_enumeration_sft.py) imports the original-source symbolic-model functions in the [full search SFT](../agents/agent50/k04_pv_early_float_triple_sft.py), checks the original two pinned SHA256 files, and asserts original spool rank15365, all four independent positions, all16 outcomes, 8+8 classification, and augmented rank15366. The preceding search includes 32 truly seeded Python-MT float positive controls; the exact 16-state enumeration was also independently derived locally.

**Critical qualification:** the selected coupon is at printer-relative native stages951..954; after inserting the new PV176 bit, **all 128 selected bits remain undetermined** (four native words with 0 individually determined bits each; selected quotient rank128). No K04 complete candidate, K08 terminal wording, or seventh REC8 slot PASS is claimed. The original acceptance, route mask, canonical candidate and verifier were not modified. Six slots still PASS, K04/K08 MISSING, combined INCOMPLETE.

**New attack opportunity:** other source-indexed `PV` values could add further independent observed-state equations once the *historical variable record-stage consumption rule* is supported on genuinely withheld original readings. Source-only fits across mostly unconstrained stages do not qualify. A second independently stage-selected PV observation with a nontrivial float residual would amplify this result and might eventually reach the selected 128-bit quotient. The original seq175 and seq177 readings are fully predicted from the printer basis and add no state rank themselves.
