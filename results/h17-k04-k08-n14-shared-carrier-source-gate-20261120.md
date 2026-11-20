# N14 cross-slot selector is not a source-authenticated shared-carrier link

**Date:** 20 November 2026  
**Agent:** 35  
**Status:** adversarial source gate; no recovered component  
**Reproducer:** agents/agent35/n14_cross_slot_source_gate.py

## Question

Does the convergence of the K04 route mask and K08 desk nonce on selector 14 establish that the selected PS-0417 coupon/render carries Gabriel's N14 sunrise photograph, or that this photograph carries Emily's final keeper caption?

## Frozen reproduction

The review reused the exact reducer in the existing K08 low-bit routing report: take the least-significant bit of each input byte in byte order, pack each group of eight with the first bit as bit 0, render the resulting two bytes as four uppercase hexadecimal characters, then pack the ASCII low bit of each character in the same first-bit-as-bit-0 order. The output is a four-bit selector.

The reproducer reads the six accepted values from candidate.json, K04/K08 constants from recovery-routing.json, and only the exact PS-0417 / ESC-S / WATCH-SPARE spool rows needed for matched controls. It does not read acceptance commitments or inspect image content.

### Eight slot inputs

| Input | Packed bytes | Selector |
|---|---:|---:|
| K01 | 0479 | N12 |
| K02 | F961 | N10 |
| K03 | 251C | N14 |
| K05 | 0343 | N10 |
| K06 | 8345 | N10 |
| K07 | 87CC | N14 |
| K04 masked component | D939 | N14 |
| K08 desk nonce | F797 | N14 |

The N14 result is not specific to the two missing slots: **four of eight** slot inputs select N14, including already accepted K03 and K07. K02/K05/K06 select N10 and K01 selects N12. This is a nontrivial cross-slot address cluster, not a missing-slot-only convergence.

### Matched 16-byte spool control

The same reducer was applied to all 133 retained 16-byte PAYLOAD fields in spool-reconstruction.log, without using acceptance commitments:

| Selector | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Count | 11 | 3 | 7 | 12 | 2 | 13 | 7 | 10 | 9 | 10 | 8 | 5 | 13 | 6 | 7 | 10 |

N14 occurs in only **7/133** spool payloads (5.26%); N10 occurs 8/133 and N12 13/133. The selected PS-0417 attempt-2 ACK itself selects 5, and its ACK2 XOR K04 mask selects 1. As a descriptive matched-control calculation, a sample of eight drawn without replacement from these 133 payloads would contain at least four N14 selectors with probability 0.0182%. The eight slot inputs are not a random sample from the spool population, so this is not a p-value; it does show that N14 is not simply a high-frequency output of the reducer on arbitrary retained payloads.

The 4/3/1 slot occupancy (N14/N10/N12) is also unusual under an iid-uniform four-bit selector null: the probability that any of 16 values receives at least four of eight inputs is 1.3928%, and the probability of an exact 4/3/1 occupancy pattern across any three values is 0.0219%. These are descriptive null calculations, not p-values: the second-stage reducer and note-index interpretation were explored after source inspection, and the eight slot inputs may not be independent.

For the two missing-slot constants alone, an ideal independent-uniform four-bit selector gives a collision probability of 1/16. That is only a reference calculation, not a significance claim: no source-authored rule explicitly says to apply this reducer to both constants and interpret the output as a photograph ID.

### Matched printer controls

| Retained row | Packed bytes | Selector |
|---|---:|---:|
| PS-0417 attempt 1 ACK / LABEL | 3D45 | 9 |
| PS-0417 attempt 1 REQUESTED / RECOVER | ED78 | 5 |
| PS-0417 attempt 2 ACK / RECOVER | 3BED | 5 |
| PS-0417 attempt 3 REQUESTED / RECOVER | 360D | 1 |
| PS-0420 attempt 1 ACK / STORES | BFE3 | 12 |
| PS-0420 attempt 2 ACK / RECOVER | CD67 | 9 |
| PS-0448 attempt 1 ACK / RECOVER | 1714 | 7 |
| PS-0417 attempt 2 ACK XOR K04 mask | E2D4 | 1 |

Neither the selected ACK2 payload nor its direct route-derived XOR candidate selects N14. This is only a selector control: MAIL-16 explicitly says the ACK is dispatch evidence, not a media-integrity flag, so it cannot identify the physical coupon or rule out a different rendered object.

## Source relationship assessment

The surviving records do not provide a source-authored join from N14 to PS-0417 or from N14 to Emily's final caption:

- The crew-note export identifies N14 as Gabriel's “Sunrise photograph”. N10 is Emily's desk note and refers to “the photograph after the last cup”; it does not name N14. MAIL-11 says Emily used desk notes and photograph captions, but does not identify which photograph or version supplied the final envelope words.
- MAIL-14 says the photographs and galley captions were deliberately kept separate from the WN-14 engineering procedure. WN-14 is the signed watch register; N14 is a numbered crew-board note. The shared number “14” is not a document identity.
- The route sheet defines K04 as the escrow coupon on logical route ESC-N and K08 as the keeper's desk phrase. MAIL-16 identifies ESC-N as the north coupon for the masked component and cautions that the ACK is not a media-integrity flag.
- The print-fleet return note maps PS-261003-0417 to ESC-N / L-29/N / FA-17 / H17-POL-17/A3. PTW-417 separately requests a cosmetic-corrosion photograph, and MAIL-04 says its paperwork was reopened for a photograph. Neither source identifies that image as N14 or as Emily's late-watch photograph. The common “417” suffix is not a direct job/permit foreign key.
- The additional N20 HMAC-to-N14 edge in the existing low-bit cycle is conditional on stripping colon-prefix labels from note text. The same report's full-label control changes 18/24 note selectors, including N14, and removes the four-note attractor. The K04-mask/K08-nonce constant calculation is separate from this parser-sensitive note-HMAC graph.

These facts leave open the possibility that a future native object contains an image, but they do not establish that it is the N14 photograph or that Emily used it for the recovery-envelope caption.

## Decision

**Do not admit N14 as the target image or run the frozen decoder against an unrelated image on the basis of selector convergence alone.** Keep Agent50's decoder pre-registration conditional. A valid future test requires an independently preserved image plus source metadata tying it to N14, and a separate source-authored link from that image/version to Emily's final envelope wording. If the native PS-0417 job is acquired for K04, inspect its complete document/rendered output as a distinct K04 media intake; do not assume it is the N14 image or the K08 caption carrier.

K04 and K08 remain separate acceptance problems. This review neither recovers nor falsifies either component. No source, candidate, acceptance commitment, verifier, or workflow was changed.

## Reproduction

From a repository checkout:

    python agents/agent35/n14_cross_slot_source_gate.py --evidence-dir resources/evidence --candidate candidate.json

The same script was locally executed against the uploaded archive's evidence directory and the current six-value candidate. Its output reproduces both tables above.
