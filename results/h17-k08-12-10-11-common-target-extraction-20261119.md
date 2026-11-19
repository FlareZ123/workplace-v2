# K08 MAIL-12/N10/N11 email-body routing control: N13 is non-discriminating

**Agent 25 | 19 November 2026 | null calibration, not a new phrase candidate**

## Prior-art correction

The exact normalized N13 caption below was already rejected by Agent6 on 7 November:

- `results/h17-k08-n13-exact-caption-candidate-negative-20261107.md`

The note edges N10→N13 and N11→N13, and the common four-note cycle, were already established by Agent9:

- `communications/broadcast/20261119T0550Z_agent9-k08-hmac-lowbit-cycle.md`

Therefore neither the N13 wording nor those note-graph edges are new findings. This report's only additional contribution is a matched-control test of extending the same HMAC-low-bit reducer to the selected MAIL-12 email body and to all 20 email bodies.

## Frozen control

The source order is **MAIL-12 → N10 → N11**, corresponding to selectors 12/10/11. The fixed operation is:

1. Normalize each complete source body with the existing K08 lowercase/alphanumeric-whitespace normalizer.
2. Apply the existing K08 HMAC16 → low-bit-pack → uppercase-hex → low-value reducer to each body.
3. For MAIL-12, this is an explicit extension of the note router to an email body, not an authenticated historical rule.
4. Follow each output through the already-known note graph.
5. Report the first common note and apply the unchanged K08 commitment to its complete body. No phrase edits or variants are permitted.

MAIL-12 says a small card was placed by the shelf. N10 is Emily's desk-copy/photo-reference note; N11 is David's mug-shelf note. The email body is used only for this reducer control; its content does not establish the physical card's words.

## Route and already-known candidate

| Source | HMAC16 | Low-bit packed hex | Selector | Path to common note |
|---|---|---|---:|---|
| MAIL-12 body | `58095245C3EB6321E16302F9D79A8A13` | `FA9B` | 6 | 6 → 10 → 13 |
| N10 body | `8FAF682BE3F69E63BB7361661AE4DDFB` | `9BC7` | 13 | 13 |
| N11 body | `0A0146B670268BCF17BD9810128B95FB` | `C2E3` | 13 | 13 |

The first common note is N13. Its complete normalized body is the previously rejected candidate:

`at the end of the night the mugs stood beside the window and somebody had remembered to leave the little lamp on`

The already-known K08 computation is:

- Candidate HMAC16: `26076C5426016BDB768A2B83E9F36857`
- SHA-256 of candidate HMAC16: `33e430295cb8ba51e8432fdab4a4da518c89ea8ee71dd2d3dc9fe09ee74f3d20`
- Required K08 SHA-256: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`
- Outcome: **no match**, as Agent6 already recorded.

## New specificity control

The same email-body extension was applied once to each of the 20 retained email bodies, then each selector was followed through the unchanged note graph. **19 of 20** email bodies reach N13.

| Edges to N13 | Email bodies |
|---:|---:|
| 0 | 2 |
| 1 | 3 |
| 2 | 6 |
| 3 | 5 |
| 4 | 2 |
| 5 | 1 |

This is the new observation. The MAIL-12→N06→N10→N13 path is not a discriminating locator: almost every email control reaches the same target because the note graph converges on its common cycle. The email-body extension therefore supplies no evidence for the final envelope wording.

## Evidence pins and limits

The reproducer pins these SHA-256 values, matching the supplied archive and repository resource blobs:

- `evidence/crew/noticeboard-and-desk-notes.txt`: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- `evidence/mail/12.eml`: `4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd`
- `evidence/recovery-routing.json`: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- `acceptance.json`: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

This test does not establish that MAIL-12 is a valid HMAC note node, that N13 is an envelope version, or that the physical shelf card contains N13's text. It only demonstrates that applying the note reducer to email bodies produces a generic convergence. K08 remains MISSING; K04 remains independently unresolved; REC8/1 remains INCOMPLETE.

## Reproduction

From the repository root:

```bash
python agents/agent25/k08_12_10_11_common_target_sft.py
```

The script validates the pinned evidence, emits the three selected routes, the previously rejected candidate's commitment outcome, and the 20-email control distribution. It does not write to source evidence, `candidate.json`, or `verify.py`.

**Decision:** retain this only as a null-calibration result. Do not count N13 or the note-graph convergence as a new recovery, and do not add more email-body routing variants. A future K08 result must come from an independently discriminating complete phrase or an authenticated native carrier.
