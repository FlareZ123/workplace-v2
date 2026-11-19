# K08 12/10/11 common-target text extraction: N13 rejected

**Agent 25 | 19 November 2026 | finite, source-pinned extraction test**

## Question and pre-registered rule

Can the 12/10/11 selector set, applied to the retained MAIL-12, N10 and N11 text fields, recover a complete candidate phrase without free-form phrase generation?

Before consulting the K08 commitment, the test fixed the following operation:

1. Use source order **MAIL-12 → N10 → N11**, corresponding to selectors 12/10/11.
2. Normalize each complete source body using the existing K08 lowercase/alphanumeric-whitespace normalizer.
3. Apply the existing K08 HMAC16 → low-bit-pack → uppercase-hex → low-value reducer to each body. For MAIL-12 this is an explicit extension of the note router to an email body; it is a hypothesis, not an authenticated historical rule.
4. Follow each resulting note selector through the existing HMAC note graph until the first note common to all three paths.
5. Use that common note's complete body as the sole candidate. Do not splice, paraphrase, reorder, or repair it.

MAIL-12's physical-card statement is retained as context: it says a small card was placed by the shelf. N10 is Emily's desk-copy/photo-reference note; N11 is David's mug-shelf note. No text from the physical card is inferred.

## Frozen route and candidate

| Source | HMAC16 | Low-bit packed hex | Selector | Path to common note |
|---|---|---|---:|---|
| MAIL-12 body | `58095245C3EB6321E16302F9D79A8A13` | `FA9B` | 6 | 6 → 10 → 13 |
| N10 body | `8FAF682BE3F69E63BB7361661AE4DDFB` | `9BC7` | 13 | 13 |
| N11 body | `0A0146B670268BCF17BD9810128B95FB` | `C2E3` | 13 | 13 |

The first common note is **N13**, an Emily-authored scene note. Its complete normalized body is the candidate:

`at the end of the night the mugs stood beside the window and somebody had remembered to leave the little lamp on`

The unchanged K08 computation gives:

- Candidate HMAC16: `26076C5426016BDB768A2B83E9F36857`
- SHA-256 of candidate HMAC16: `33e430295cb8ba51e8432fdab4a4da518c89ea8ee71dd2d3dc9fe09ee74f3d20`
- Required K08 SHA-256: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`
- **Outcome: no match.**

The full phrase was fixed before the acceptance comparison. No candidate or verifier file was modified.

## Specificity control

The same HMAC extension was applied once to each of the 20 retained email bodies, then each output was followed through the unchanged note graph. **19 of 20** email bodies reach N13. The edge-distance distribution is:

| Edges to N13 | Email bodies |
|---:|---:|
| 0 | 2 |
| 1 | 3 |
| 2 | 6 |
| 3 | 5 |
| 4 | 2 |
| 5 | 1 |

The selected MAIL-12 path is therefore not a discriminating locator: the note graph's common cycle causes nearly every email control to reach the same target. The N10/N11 convergence is deterministic but does not identify the final envelope wording.

## Evidence pins and limits

The reproducer pins the following SHA-256 values, all matching the supplied archive and repository resource blobs:

- `evidence/crew/noticeboard-and-desk-notes.txt`: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- `evidence/mail/12.eml`: `4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd`
- `evidence/recovery-routing.json`: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- `acceptance.json`: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

This test does **not** establish that MAIL-12 is a valid HMAC note node, that N13 is an envelope version, or that the physical shelf card contains N13's text. It only rejects this one complete, deterministic candidate. K08 remains MISSING; K04 remains independently unresolved; REC8/1 remains INCOMPLETE.

## Reproduction

From the repository root:

```bash
python agents/agent25/k08_12_10_11_common_target_sft.py
```

The script reads the original routing and acceptance files, validates the pinned evidence, emits all three selected routes, the complete normalized candidate, the original commitment outcome, and the 20-email control distribution. It does not write to source evidence, `candidate.json`, or `verify.py`.

**Decision:** close this N13 extraction hypothesis. Do not add more email-body routing variants or promote the common-cycle convergence as independent evidence. A future K08 text result must be an independently discriminating complete phrase or an authenticated native carrier, not another traversal of the same note cycle.
