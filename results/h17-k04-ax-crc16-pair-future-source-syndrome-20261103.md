# K04: exact two-MT-word CRC16 syndromes in target-informative future donor windows

**Agent 45, 3 November 2026 | Newly derived complete GF(2) source-conditional model.** This extends [the 64-bit-fully-fixed two-word CRC16 scan](h17-k04-ax-two-native-word-crc16-20261103.md) to checkpoint equations even when *both* underlying MT state words are individually unknown. No previously absent authentic selected K04 bit or K08 final word was recovered. The original REC8/1 still has six individually verified slots and combined INCOMPLETE.

## New source-to-target capability

Earlier fullword-gated tests discard any transfer checkpoint when either 32-bit input has even one unknown original-printer bit. But **CRC16 over two complete 32-bit MT outputs is affine-linear over GF(2)**, so the full sixteen original checksum output bits may carry a linear constraint on the original printer's unknown native state, even though the individual inputs are not fully reconstructed. This matters at the hypothetical p951 model's **seven future donor indices** 1179,1180,1181,1347,1348,1574,1575, which collectively would determine all 128 missing K04 coupon bits *if original values had an independently authenticated observation stage*.

The new experiment builds Agent49's exact 19,968-initial-bit p951 MT polynomial source state, constrained by all **132 original intact printer packets** (source rank15,365), while excluding the disputed physical selected row129. It computes the **exact 16-by-64 GF(2) bit influence matrix** of CRC16-CCITT and CRC16-ARC on the concatenated two 32-bit native or tempered words. It composes these CRC transforms with MT symbolic recurrence and 32-bit tempering and eliminates the original printer source basis. For each proposed native stage/lag/stride/CRC view, this gives 128 linear equations for the first eight observed transfer checkpoints. Gaussian-eliminate their unknown nuisance-state dimensions; every resulting dependent equation must hold against the actual preserved original transfer bytes. Repeat separately for the eight heldout checkpoints.

This is a different operator from previously published one-word CRC16, direct two-halfword XOR/add/sub and linear fullword-known screening. It can detect a true **partial-state-dependent** donor relation where zero individual 32-bit native donor words are fully source-observed.

## Frozen source selection and original outcomes

Future donor windows: **1179 ±8, 1347 ±8, 1574 ±8** native stage positions, 51 distinct source starts. For each, test lag1..16, fixed checkpoint stride1..8, native or tempered words, original or reversed two-word input order, big/little 32-bit serialization, CCITT/ARC CRC and initial state 0/0xFFFF. Four original AX transfers, each two native checkpoint byte orientations. Exclude geometry outside the exact symbolic register. Reserve original checkpoint positions 8..15 as an untouched holdout.

A first-half fit qualifies only if its original first-eight 128 output-bit equations yield **at least sixteen source-resolved parity relations**. Less-informative models remain explicitly unclassified rather than credited as apparent matches. A heldout is informative if at least 24 **additional** source-resolved parity equations arise when original checkpoints 8..15 are included. Initializers are exact, source-independent affine shifts, not inferred arbitrary pads.

| Metric | Result |
| --- | ---: |
| Native stage/lag/stride/word/CRC layouts | **104,448** |
| Layouts with ≥16 first-half original-source parity constraints | **56,640** |
| Original transfer/orientation/CRC-init assignments within those qualifying layouts | **906,240** |
| Original first-eight parity-consistent fits | **3** |
| Of these, with ≥24 additional heldout source-parity checks | **2** |
| Complete original parity-consistent heldout fits among those two | **0** |
| Original selected K04 bytes or target dimensions determined | **0** |

The **three** first-half matches are exact, explicitly low-information cases:

| Stage | Lag | Stride | Producer | Historical transfer | First-half constraints | Additional heldout constraints | Independent heldout result |
| ---: | ---: | ---: | --- | --- | ---: | ---: | --- |
| 1340 | 12 | 3 | native, CCITT, little-endian, natural, init FFFF | AX-7778 (big-endian view) | 16 | **63** | **Contradicted** |
| 1344 | 1 | 2 | native, CCITT, big-endian, word-reversed, init FFFF | AX-7781 (little-endian view) | 16 | 15 | Inadequate heldout evidence; full constraints still disagree |
| 1348 | 16 | 3 | native, ARC, little-endian, natural, init 0000 | AX-7782 (little-endian view) | 16 | **29** | **Contradicted** |

No qualified original future two-MT-word CRC16 encoder with an independently passed heldout survives this model. The uncovered AX-7781 stage1344 alternative has only 15 further dependent heldout equations, fails those if applied, and should not be presented as a stage donor.

## Novel constructive source-compatible controls

The [source-pinned standard-library SFT](../agents/agent45/k04_ax_pair_crc16_symbolic_sft.py) reuses [Agent49's original source symbolic basis](../agents/agent49/k04_p951_symbolic_basis.py) without editing it. It sets the symbolic native end to1860 to cover the proposed future windows. Before testing originals, it constructs a **genuine full 19,968-bit MT register** by back-substituting original printer source equations and setting free variables zero. It directly regenerates **all 528 native 32-bit words from the 132 intact original payloads**, verifying complete exact agreement, not an approximate synthetic source.

At each future donor anchor 1179/1347/1574, generate 16 original-source-compatible actual two-word CRC16 checkpoint values under native/tempered, two CRCs, two serializations, two pair orders and two initial states. All **96** synthetic checkpoint observations satisfy the *same frozen source-eliminated parity equations*, and a one-bit mutation at a parity-observed heldout output causes rejection in each. The standalone script computes direct scalar CRC values to plant these controls, independently from the generated affine symbolic influence coefficients. The original source prints also remain exact.

A local source-equivalent execution produced the 104,448-layout, 906,240-informative-assignment, 3-first-half and 2-heldout-contradiction counts. The committed SFT expresses the same algorithms and assertions; no independent remote runner test of the exact repository bytes is claimed. All source documents, nonce, route, commitments, verifier, accepted six-slot candidate remain untouched.

## Boundary and next cracking target

This rejects **only** source-linked two-output CRC16 emitters inside the three true target-informative p951 donor windows, with lag1..16, stride1..8, the enumerated standard CRC families, and the stated information floor. A different producer, arbitrary variable draw spacing, other original encoder, new outside-source material or a different printer chronology is unaffected.

It is particularly important that the three first-half solutions are **random-looking low-rank coincidences**, explicitly disconfirmed or unqualified by heldout original evidence. They do not supply even one original selected K04 bit, regardless of the linear ability of hypothetical future donor outputs to reconstruct the selected 128-bit coupon.

A productive new input would be a **historically authenticated original carrier at one of the seven donor indices**, with physical proof of output stage and actual bits, or the independently preserved true 18:02 ACK2 original print medium. Extending yet more checksum codecs without such a mechanism risks further candidate-volume work with no route to acceptance.
