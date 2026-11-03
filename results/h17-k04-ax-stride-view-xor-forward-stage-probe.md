# K04: cross-transfer 16-bit emitter and XOR-salt probe through native MT index 5300

**Agent 1, 3 November 2026. Source-conditional original-data experiment. K04 remains missing.**

## Question and distinctness

Could any surviving AX-7781, AX-7782, or AX-7783 checkpoint series disclose a previously unobserved, target-informative section of the speculative common MT19937 source that fits the 132 retained intact printer coupons? The earlier [Agent50 study](h17-k04-six-geometry-ax-7778-source-selection-and-grid-coupon.md) selected AX-7778's 16 upper-halfword checkpoints at p951 native start −157, but its other-transfer whole-window test required contiguous output positions within −1100..1025. This extension tests **all constant strides 1 through 16**, a native-stage horizon through **5300**, all four high/low×native/tempered 16-bit output views, both checkpoint byte orders, and a **transfer-specific fixed 16-bit XOR whitening salt** inferred from the first eight checkpoints.

This is a defined family of alternative source generators, **not** an assertion that transfer firmware uses MT19937, a fixed stride, or XOR whitening.

## Exact test

Reproduce from the unmodified repository with [the standalone test](../agents/agent1/k04_ax_extended_source_sft.py), which imports [Agent49's independently pinned printer symbolic model](../agents/agent49/k04_p951_symbolic_basis.py). It excludes disputed printer row129 *before* constructing equations and reads the unchanged original transfer-audit bytes, SHA256 `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`. All 16 checkpoint values per transfer are sorted by (seq,attempt). Each proposed output maps to either 16 native-state bits or 16 tempered-state bits, with high/low half and global byte order fixed over the series.

For every candidate alignment, infer compatibility from **only the first eight original checkpoints**, requiring either (a) ≥32 source-fixed agreement bits and no contradictions for direct emission, or (b) ≥24 source-fixed *redundant* agreement bits after estimating a common 16-bit XOR salt. Compare the remaining eight original checkpoints separately. Native positions span −1100 through 5300, and a 16-sample sequence must fit fully inside that bound.

## Original-source results

| Transfer | Direct source-consistent alignment | Constant-XOR source-consistent alignment |
|---|---|---|
| AX-7778 | **One**, tempered upper16, byte-swapped, stride1, native start −157; first8 **45/45** fixed bits, heldout8 **77/77** | **Same alignment**, salt `0000`; 29 first8 redundant bits and **77/77** heldout bits |
| AX-7781 | **None** | **None** |
| AX-7782 | **None** | **None** |
| AX-7783 | **None** | **None** |

The sole detected relation reproduces Agent50's positive **without using the withheld eight values for stage selection**. The XOR-salt extension supplies a genuinely different whitening hypothesis and a positive control at zero salt. The fresh extended-stage and view tests produce no second transfer-source alignment, including no AX-7782 donor capable of constraining the selected printer coupon under these specified generation families.

## What this excludes and what it leaves open

The negative covers **only** the listed constant-stride, single-16-bit-output-per-checkpoint, fixed-view and optional fixed-XOR models **when the first eight observations have the stated minimum informative overlap with independently preserved intact printer bits**. It cannot exclude weaker-overlap stages, variable gaps, more complex encodings, separate generator initializations, or a later region beyond index5300. The AX-7778 positive reinforces a conditional source relation, but the historical producer, printer chronology, and physical ACK integrity remain unauthenticated. Other documented CLASS and timestamp sampler contradictions are unaffected.

This investigation gains **zero independently authenticated bits** of the 128-bit selected K04 coupon and does not recover Emily's exact K08 words. The original source files, route mask, candidate, commitments, and verifier are unchanged. The six previously passing components still pass individually; combined REC8 recovery remains incomplete.

**Research implication:** stop treating the other three checkpoint transfers as obvious contiguous/regular source donors in the tested state horizon. A future attempt should specify a different emitter/data-dependency model with a discriminating original-source heldout, or investigate a stronger producer-stage relation.