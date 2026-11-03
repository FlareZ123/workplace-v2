# K08 purpose-conditioned envelope editor: a discriminating two-label calibration with an overfit ablation

**Agent 10 | 3 November 2026.** This is a new complete-candidate construction using a finite word-level grammar and an explicit purpose-dependent rank function. It follows Agent14's source-masked genre control, but supplies a **joint numerical rank comparison** and explicitly measures how the visible labels contaminate hindsight tuning. No original K04 or K08 component was recovered.

## Original-source inputs and leakage control

Source: original crew note extract SHA-256 \`13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb\`, all 20 original emails, \`evidence/recovery-routing.json\`, and original \`acceptance.json\` in the surviving archive. Known full envelope inscriptions N17 and N18 were withheld from the source vocabulary **in both places they occur**, including their MAIL-11 quotes (N18's quote omits the note's final period). The program asserts neither normalized full phrase survives in the masked source documents. There is no hidden original beyond the supplied export.

The *same fixed* 21,836 complete normalized candidate phrases are rendered for all purposes. Syntax includes an imperative action/object/state/recipient frame, a temporal-return/first-or-last-event frame, and two-breath scene/crew-condensation frames. Individual vocabulary fields and editorial templates are **human-curated after investigators knew the label texts**; therefore admitting both labels establishes grammar coverage, **not a blind predictive achievement**. Scores depend on purpose-selected *surviving* context documents, bounded word relevance, missing-source-token penalties, observed bigram bonuses, and shared envelope length/style costs.

The executable [SFT](../agents/agent10/k08_purpose_editor_sft.py) uses the original normalization/HMAC/slot-SHA relation, checks N02's independently known HMAC derivative, and validates a planted complete candidate against the same synthetic slot-hash procedure. It never modifies the originals.

## Results: unassisted source-context ranking

| Known actual label | Correct purpose rank | Shuffled standby rank | Shuffled commissioning rank | Shuffled keeper rank |
| --- | ---: | ---: | ---: | ---: |
| N17 standby: \`leave the light on for the next watch\` | **3,193 / 21,836** | self | 7,525 | 11,944 |
| N18 commissioning: \`back before the first boat\` | **762 / 21,836** | 13,186 | self | 15,996 |

The top-1,000 intersections were **157** between standby and commissioning, **428** between standby and keeper, and **155** between commissioning and keeper. This indicates some purpose-specific ordering beyond a completely identical generic candidate cover, although a rank of 3,193 for N17 is not selective enough for a strong terminal-caption extrapolation.

**Direct K08 check:** all **21,836 unique complete phrases** rejected by the untouched original K08 slot commitment; **0 accepted**. The nonce is decoded from the original route sheet; normalized candidate text is HMAC-SHA256 truncated to 16 bytes, and the accepted slot digest checks SHA256 of those 16 bytes.

## Hindsight-word-assisted ablation

To measure retrospective leakage directly, the \`--assisted\` variant adds **manually supplied purpose keywords** that overlap the visible target labels. These are explicitly *not* allowed to count as independent source evidence.

| Control | Context-only rank | Target-word-assisted rank | Assisted wrong-purpose rank |
| --- | ---: | ---: | ---: |
| N17 standby | 3,193 | **492** | 8,079 (commissioning) |
| N18 commissioning | 762 | **10** | 14,148 (standby) |

Assisted top-1,000 intersections fall to 88 (standby/commissioning), 248 (standby/keeper), and 72 (commissioning/keeper), reflecting that the assistance forces more separation. Both assisted and unassisted runs test the identical complete phrase set, so neither finds K08.

## Decision and limitation

This particular grammar **covers** both real inscription genres and has **some genuine ranking contrast** when only surviving context is scored. However the dramatic improvement to rank 10/492 requires target-informed keywords. Thus the assisted test is an **overfit diagnostic**, and the unassisted one is a weak retrospective calibration rather than a validated author-specific edit program. An unobserved terminal caption may use any word or syntax outside these fields; 21,836 negative candidates are a conditional family exclusion only.

The next materially different test should construct and freeze an editor from **purpose-independent source features and a third blinded inscription** before using the official K08 target. If no third authentic label exists, report that evidentiary limitation rather than tuning to the two already-known inscriptions. Do not scale this fixed grammar as though low retrospective rank guaranteed recovery. K04 remains unresolved; six original slot PASS, K04 and K08 MISSING, combined INCOMPLETE.
