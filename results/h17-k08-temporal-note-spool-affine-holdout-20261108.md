# K08: note-index to printer counter-affine transport, whole-record holdout

**Agent29 | 8 November 2026 | conditional, source-only result.** A reversible complete-HMAC reconstruction architecture was implemented, with **432 original whole-record holdout checks and zero single-record passes**. The historic final keeper words and K08 component remain unrecovered. Six original slots remain PASS; K04/K08 and combined REC8/1 remain unresolved.

## Recoverable mechanism

The candidate note→printer index association Nxx→PS-261003-(0300+xx), documented separately in [the source crosswalk](h17-k08-note-spool-sequence-crosswalk-20261107.md), would give five original Emily note bodies with candidate printer pairs:

- N02, first crew-board draft → PS-0302;
- N06, second desk draft → PS-0306;
- N13, complete end-of-night scene → PS-0313;
- N17, explicit standby label → PS-0317;
- N18, explicit commissioning label → PS-0318.

The original HMAC16 for N18's actual label text is **A3100AE1ABB9C8D58315D9EBF326978B**, providing an exact published-note reduction control. All five note bodies are normalized with the unchanged desk nonce. Neither the Nxx→PS mapping nor actual printing of the N13 wording is authenticated; the preserved printer 16-byte fields carry an explicit integrity warning.

The new model asks whether a versioned 128-bit transport pad, inferred from **two intact labeled note/packet pairs**, predicts the other three original *whole 16-byte HMAC values* and can therefore decode PS-0323 (the conditional N23 final-margin source) without guessing Emily's final words. This differs from [Agent33's shared-route constant-pad K08 test](h17-k08-note-spool-same-route-pad-negative-20261107.md), which uses N18 alone and performs direct K08 target probes.

Three explicitly finite counter rules were frozen:

1. XOR pad constant by job-index **parity** (distinct odd/even pads).
2. Whole 128-bit modular additive pad affine in job index, big-endian.
3. Whole 128-bit modular additive pad affine in job index, little-endian.

For each, four fixed printer-packet word/byte views were allowed. For the affine variants, fit only **odd index-difference** pairs, making the difference invertible mod 2^128; for the parity variant, use only opposite-parity pairs. Among original N02,N06,N13,N17,N18, each of the twelve ordered opposite-parity calibration pairs yields **three independent withheld original note/packet comparisons**.

## Executed original-source and synthetic results

- **4 packet views × 3 models × 12 ordered calibration pairs = 144 fits**, each with three untouched holdout records.
- **432 complete 128-bit original holdout comparisons, zero matches.** No two-pair model predicts even one independent original source text/packet value. The K08 commitment is never used to choose a calibration.
- **12/12 planted complete-emitter controls PASS**, including blinded recovery of a synthetic final-caption HMAC16 after fitting from N17/N18 and reproducing all three other complete synthetic notes.

Original source SHA256 pins: crew notes `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`; printer spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; routing `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`; commitments `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

Reproduce using [the single-file source-pinned test](../agents/agent29/k08_note_spool_affine_transport_sft.py), from repository root:

`python agents/agent29/k08_note_spool_affine_transport_sft.py`

## Conclusion

This particular **pair-calibrated temporal transport** cannot reconstruct the conditional PS-0323 final HMAC from the five preserved Emily texts. It is an original-source calibration failure, more discriminating than a free-text sentence sweep, and it does not claim any real physical spool-to-caption relationship. Alternative source-bearing versions, a native rendered PS-0323 label, or Emily's original final margin remain open. The canonical candidate and immutable acceptance files were untouched.
