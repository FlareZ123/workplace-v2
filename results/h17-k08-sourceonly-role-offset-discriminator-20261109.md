# K08 source-only note-role to printer CLASS discriminator

**Agent 40 | 9 November 2026 | Original-source result. No K08 recovery.**

## Question and competing prediction

The current conditional locator maps Nxx to printer job PS-(0300+xx), making PS-0323 a candidate keeper-envelope source. Agent17's retrospective offset-zero evidence used CLASS/DEST expectations for N17, N18, N20, N23, N24 selected after seeing the records, including N18 as RECOVER despite the note literally describing a *commissioning envelope label*. The 9 Nov Critic called for independent role holdouts and offset robustness.

This experiment freezes **source-only printable-role cues** before consulting any printer metadata. The strict set consists of 11 note bodies explicitly presented as photographs, captions, a heading, a notice, an envelope label, or a departure board: N01, N03, N04, N08, N09, N14, N15, N16, N17, N18, N24. The conditional prediction is **CLASS=LABEL if that textual role is actually transported as a printer label**. Deliberately make no print assertion for editorial prose N10/N13/N20/N23. An extended set adds two weaker scene-location cues N05 and N11; those are reported separately.

## Whole-source test

Original crew SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`; printer SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The reproducible [source-role offset SFT](../agents/agent40/k08_note_spool_sourceclass_sft.py) asserts both digests, role-cue text, 24 notes, and the 128 ordinary ACK1 jobs PS-0300..0427. It searches all 105 valid contiguous offsets, -1..103, without fitting any role or field to the printer.

| Frozen source-only role set | Matches at offset zero | Offsets matching at least as well | Best score and offset | Exact within-24-note role-permutation upper tail |
| --- | ---: | ---: | --- | ---: |
| 11 strict printable roles | **5/11** | **48/105** | 8/11 at **+80** | 0.234710818 |
| 13 extended printable roles | **6/13** | **42/105** | 9/13 at **+80,+103** | 0.155741015 |
| 8 out-of-anchor N01..N16 roles | **3/8** | **78/105** | 6/8 at +33,+96,+103 | 0.553192444 |
| N17/N18/N24 explicitly labelled/board anchors | **2/3** | **42/105** | 3/3 at +30,+34,+80,+94,+97 | 0.249011858 |

At the proposed offset zero, **N17, explicitly labelled a standby-envelope label, aligns to CLASS=LABEL; N18, explicitly labelled a commissioning-envelope label, aligns to CLASS=RECOVER**. The eight out-of-anchor observations are N01 STORES, N03 RECOVER, N04 LABEL, N08 LABEL, N09 STORES, N14 STORES, N15 LABEL, N16 STORES. The source-only heldout set has almost no offset-zero class selectivity.

Withhold any one of N17, N18, or N24: offset zero has respectively 4/10 (67 of 105 offsets equal or better), 5/10 (39/105), and 4/10 (66/105). A planted complete 11-role synthetic offset-zero alignment is uniquely recovered by the same code.

The hypergeometric values condition on the *observed eight LABEL jobs in the 24-job offset-zero window*, randomly reassigning the fixed number of source-label roles without replacement. They are descriptive null references for this exact test, not unconditional significance levels. The 105 offset comparisons share overlapping windows. Source-role cues predict printable text only conditionally: the job's CLASS could name an operational workflow instead of its printed material, and the note's text need never have been emitted by that printer.

## Consequence for actual recovery

**Offset zero is not privileged by a consistent source-only LABEL prediction.** This distinct source-label test does not mathematically refute an independent Nxx→PS assignment, since CLASS semantics remain open. It does expose that the previous five-role 1/105 uniqueness depends on retrospective, nonuniform role-to-CLASS/DEST choices, not on a robust independently predicted printable-role signal.

Therefore **do not invert PS-0323 into the final K08 HMAC or continue transport-model searches based solely on the offset-zero role match**. A credible recovery bridge needs a demonstrated native print manifest or a producer relation that predicts a complete genuine caption/packet holdout without retrospective role fitting. The final original N23 margin remains unquoted; the observed test adds zero exact normalized K08 words. The six accepted components and original verifier, candidate and sources remain unchanged.
