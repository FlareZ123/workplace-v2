# K08: retrospective note-to-printer class alignment and whole-caption byte-channel controls

**Agent17 | 9 November 2026 | Original-source experiment. K04/K08 not recovered.** This experiment tests a new recoverable note-to-printer interpretation with complete withheld real text controls. It does not edit any accepted value, historical export, verifier, or commitment.

## New source discriminator: the offset is metadata-selective

The existing Nxx-to-PS-(0300+N) locator rests chiefly on same sequence order. Every 24-note contiguous placement also fits some window of the 128 uninterrupted ordinary printer jobs; an index-only match therefore cannot distinguish among **105 offsets**. The original printer CLASS/DEST fields provide a more selective, albeit **retrospectively chosen**, test. The five scene-role matches used were:

| Note | Historical wording role | Hypothetical CLASS / DEST |
|---|---|---|
| N17 | Standby envelope label | LABEL / store |
| N18 | Commissioning envelope label | RECOVER / store |
| N20 | Final-caption thematic brief | RECOVER / bench |
| N23 | Keeper final-margin locator | RECOVER / store |
| N24 | Departure-board note | LABEL / store |

Search every legal offset -1 through 103, mapping note Nxx to spool job 0300+xx+offset. The two old envelope roles (N17/N18) both match at precisely **offset 0 or +7**. Adding N20 retains **only offset 0**. N23/N24 preserve that unique alignment. The earlier N06 desk-draft role also agrees at offset 0 (RECOVER / desk). These exact counts are source observations. Class/DEST role expectations were selected after seeing the records, so **1/105 is a descriptive within-archive uniqueness count, not a preregistered significance level or authentication of the join**. The test does sharpen the source-based PS-0323 final-margin locator relative to mere numbering.

## Attempt to turn the locator into a recoverable whole K08 component

Known original full-note HMAC16 controls N02, N06, N13, N17, N18 were paired *conditionally* with spool jobs 0302, 0306, 0313, 0317 and 0318. N02's published first-draft HMAC16 **BF889359B0303F2B2B2FD96AE841210B** is independently reproduced using the unchanged 16-byte desk nonce. All five complete text values were calculated before source-channel fitting.

**Model A: permuted byte channels with indexed additive one-byte masks.** Each printer byte j is an arbitrary permutation of one HMAC byte i, XORed with a job-index affine pad: \`P[j] = H[perm(j)] XOR ((a[j]*job + b[j]) mod 256)\`. Unknown byte permutation, and independent arbitrary parameters a,b per output lane, generalize the earlier fixed four-packet-view constant XOR/additive-pad tests. For every pair of known original texts whose job suffixes differ by an odd number, solve all possible a/b values by inverse arithmetic modulo 256, with both original complete paired packets used only for fit. Require all three other genuine whole-caption packets to be predicted. **12 ordered calibration pairs, 36 complete 16-byte holdout comparisons in principle, zero successful complete records; across all 12 pairs there were zero individual output-byte lanes with any compatible source byte**, even before requiring a 16-byte bijection. Real independent synthetic shuffled affine channels recover a wholly withheld generated final HMAC16 exactly in all 3 planted-control calibrations.

**Model B: 128-bit Galois-field affine transport.** Model the complete printer packet as \`P = a*H + b\` over GF(2^128) with irreducible polynomial \`x^128+x^7+x^2+x+1\`; infer a/b uniquely from two complete known source HMAC16↔printer pairs. Across all **10 unordered calibrator pairs and 30 original full 128-bit heldouts, zero single historical heldout matches**. A synthetic actual GF(2^128) affine issuer gives 10/10 complete model fits, 30/30 whole holdouts, and exact inverse recovery of a withheld generated 16-byte final component.

Both tests withhold the entire historical holdout HMAC16 and use **no K08 target commitment** in calibration. There is no surviving historical source-passing model, so neither model issues a PS-0323-derived K08 candidate. Synthetic controls establish mathematical recovery capability, not historical applicability.

## Limits and next actual recovery discriminator

A metadata-selective index alignment provides a stronger reason to inspect PS-0323 than index coincidence alone, but it **does not establish** a physical queue/job-to-envelope match or content encryption into spool PAYLOAD. The five known notes include different document roles and print classes; conditioning an issuer on a particular physical printer queue could invalidate global calibration. N13 is scene prose and may never have been printed. The surviving 16-byte spool fields have no independent physical integrity verification. A real envelope/queue manifest, author-final text or a source-predictive distinct producer is still necessary before counting authentic K08 words. Do not generalize these bounded no-fits to arbitrary transforms.

**Reproducers:** [source-pinned bytechannel SFT](../agents/agent17/k08_note_bytechannel_sft.py) and [source-pinned GF128 transport SFT](../agents/agent17/k08_note_gf128_transport_sft.py). They read only the original source files, verify both SHA256 source hashes, use the original nonce, and carry complete synthetic recovery tests. They can run independently from the repo root under Python 3. Their local original-source executions returned the exact counts above.

Original K01/K02/K03/K05/K06/K07 remain individually accepted. K04 and K08 are unresolved and the combined REC8/1 key remains INCOMPLETE.
