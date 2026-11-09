# H-17 K04: 128 ordinary printer packets plus five late rows, systematic RS source test

**Agent 4 | 9 November 2026 | Original K04 NO_MATCH; no new accepted component.**

## Complete-object hypothesis and its independent discriminator

The unchanged original printer reconstruction contains exactly **128 chronological five-minute normal ACK packets** (job suffixes 0300–0427) followed by five exceptional records: same-job PS-0417 RECOVER REQUESTED1, selected ACK2, REQUESTED3, and full ACK packets PS-0448 and PS-0420. This is a potentially meaningful **128 data rows + 5 check rows** structure. A shortened byte-lane Reed–Solomon code would reconstruct the **entire 16-byte selected coupon without reading any selected ACK2 payload**, if the complete source check rows agreed. A code model produces a 16-byte candidate which is XORed with the *original* K04 route mask and compared against the unchanged full original K04 SHA256 commitment.

The original company records **do not describe an RS encoder, five parity rows, generator polynomial, or a relationship between the otherwise distinct late print jobs.** The two late nonselected ACKs are retained copied buffers, still not independent media-certified originals; REQUESTED rows are excluded from the stringent two-control qualification. This is a novel exploratory producer hypothesis, not proof of archival coding.

## Exact locally executed source-first test

Original source: `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Original route XOR mask `8556C8CB6140A7F9A5123AC7571BEE1C`. Original K04 SHA256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. No physical or copied selected row payload is used to form a candidate.

1. **Systematic parity**: 128 source bytes per original byte lane, appended five GF(256) parity symbols by polynomial division with `g(X)=product(X+alpha^(root+i),i=0..4)`. Field polys `0x11d,0x11b`; alpha `2,3,5`; root positions `0,1`; forward/reverse source-row and parity positions. **48 complete five-row encodings.**
2. **Evaluation RS interpolation**: 128 intact source row/lane values interpreted as degree-at-most-127 polynomial evaluations. Extrapolate five complete packets at successive independent coordinates. Field polys `0x11d,0x11b`; integer indexes or distinct `alpha^i` for alpha2/3/5; forward/reverse source order. **10 legal complete five-row encodings.** Primitive-power coordinate sets with repetition were excluded.
3. Every model predicts full PS-0448 and PS-0420 copied ACK packets *withheld from construction*, then a full selected 16-byte coupon. The selected complete component is reduced using the original mask and checked against all 256 original commitment bits. REQUESTED1/3 predictions are diagnostics only.

**Source and target outcome:**
- **58** complete original K04 component comparisons, **zero original matches**.
- **0/116** complete independently retained late ACK holdout packet predictions (two per model). The strongest evaluation model agrees in only **2 of 32 bytes** across both ACKs; systematic parity models best **1 of 32**.
- All five late rows are derived per model, but no source trace establishes they are parity, so these failures constrain only the modeled RS encodings.

**Controls:** independently generated degree-127 GF256 polynomials at 133 coordinates reproduce all five unseen evaluation symbols under both field polynomials. Independently generated 128-byte per-lane systematic packets plus five parity symbols have zero generator-root syndromes and reproduce a complete 16-byte synthetic coupon and full masked-component SHA256 control. Source file SHA and exact 128+5 headers are asserted. The actual local branch also checked the complete original K04 commitment for all 58 candidates; genuine hits zero.

Reusable read-only [standalone SFT](../agents/agent4/k04_rs128_five_late_wholepacket_sft.py), Python standard library, with synthetic codeword checks and original complete commitment checks. Original `resources/`, accepted values, canonical candidate and verifier were untouched. The locally executed scratch pilot and published equivalent SFT use the same GF field, RS polynomial, 128 source packets and 58 candidate selections.

## Decision

The superficially suggestive 128+5 shape does not carry the selected coupon via these ordinary standard or evaluation RS conventions, and neither authentic copied late ACK can be reconstructed whole. Do not expand to arbitrary nonsource-defined generator matrices: 128 fully random-looking 16-byte rows can fit any desired missing 128-bit target with a free parity operator, which only restates preimage search. A distinct historical encoder or physical integrity witness would be needed before investing in more parity transforms.

**Official result remains K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined REC8/1 INCOMPLETE.**
