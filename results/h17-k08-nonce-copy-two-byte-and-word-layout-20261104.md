# K08 alternate nonce-copy interpretation: nine original texts × two-byte exhaustive repair

**Agent 12 | 4 November 2026 UTC. Status: original K08 commitment NO_MATCH; no recovered author-final phrase.** This is a speculative route-sheet transcription-fault hypothesis, explicitly distinct from the established phrase-only searches. No original source claims the desk nonce was corrupted. The purpose is to test whether one of the **already preserved source statements** would become an accepted keeper component if the transcribed 128-bit HMAC key had suffered a small copying defect.

## Source and construction

The unmodified 46-member H-17 ZIP supplies crew-note SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, route-sheet SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`, and original acceptance SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

The actual transcribed nonce is `5F933DA6A1BD03C32DA5CBC25344F497`. For nine complete original texts, apply the official lowercase ASCII-alphanumeric-whitespace normalization and HMAC-SHA256(first 16 bytes), then SHA256 the 16-byte K08 component and compare **all 32 digest bytes** with the untouched original target `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

Texts checked, with note provenance: N01 (sea/tea photograph), N02 (first authored board draft), N06 (second authored desk draft), N09 (Zoey's first-cup caption), N13 (mugs/window/lamp scene), N17 (standby label), N18 (commissioning label), N20 (Emily's triad and standby warning), N23 (Emily's final-margin *description*, **not a verbatim margin**). The caption portion after the label was used for N01/N02/N06/N09/N17/N18. For N13/N20/N23, the original complete note sentence(s) were used; these three descriptive records are **not** asserted to be the chosen final phrase.

## Complete fault family and executed result

Keep any fourteen of the sixteen nonce bytes unchanged and replace **any one or two other byte positions** with arbitrary non-original values. Per complete normalized text, test:

- unchanged original nonce: one candidate;
- one changed nonce byte: `16 × 255 = 4,080` candidates;
- two distinct changed nonce bytes: `120 × 255 × 255 = 7,803,000` candidates.

That is **7,807,081** checks per text, **70,263,729 complete candidate checks across nine texts**, of which **70,263,720** have altered nonce bytes. All original full K08 commitments rejected. The executed OpenSSL C reproducer is [Agent12 K08 nonce-fault SFT](../agents/agent12/h17_k08_nonce_fault_sft.c). It reports `NO_MATCH start=0 checks=7807080` for each normalized text and `SELFTEST synthetic two-byte nonce mutation PASS` for an independently constructed two-position changed nonce. The nine full source tests were executed locally on the original ZIP-derived text; the code was committed after the tests and its remote contents read back.

A second, much cheaper and **nonoverlapping full-layout** test allowed all `4! × 4! = 576` transformations of the four 32-bit nonce words: arbitrary wholeword order, with one shared four-byte permutation applied to *every* word (including endian reversals). Each transformed nonce was HMAC-tested against each of the nine same texts: **5,184 complete candidate checks, zero original K08 matches**. This script was executed locally, and the scope is fully specified here. These were test assignments, not assertions that the original nonce was serialized incorrectly.

## What changes

The original nonce is no more likely to be corrupted just because this model was tested. Rather, these results close one **alternate, complete-candidate construction** under which the visible drafts/notes could have been the accepted keeper caption despite a damaged HMAC key. A changed nonce affecting three or more bytes, a nonuniform byte permutation, a different source phrase, or a different key-derivation scheme remains untested. No test authenticates Emily's author-final margin; no K04 target bit is gained. **K01/K02/K03/K05/K06/K07 still PASS; K04/K08 unresolved; combined REC8/1 INCOMPLETE.**

Do not infer that the caption is an existing source sentence or that a nonce copy defect occurred. The next useful attack should target a previously overlooked author-final phrase carrier or a source-selected transformation that predicts full text, rather than widening these unsupported nonce defects.