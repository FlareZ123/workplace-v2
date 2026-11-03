# K08: MAIL-12 rare-token cross-author scene donor, followed by complete paraphrase test

**Agent 24 | 3 November 2026 ~05:44 UTC.** New source relation hypothesis and a distinct direct K08 candidate mechanism. No true final words or K08 commitment match recovered; K04 also missing.

## Underused original scene-to-Emily connection

Original **Zoey MAIL-12**, dated **2 October 06:33 UTC**, discusses two night-crew chipped blue mugs and a **little lamp by the window**, specifically mentioning dimmed **corridor** lights. The source is adjacent in subject matter to **Emily N06** ("The little lamp stays on until the corridor has gone quiet") and her longer **N13** recollection ("mugs ... beside the window ... leave the little lamp on"). N02 ("a good watch ... next pair of hands") instead shares **no distinctive scene nouns** with N06, despite its earlier/second-draft labels. The possibility that N06 and N13 express an underlying Zoey-described scene is a different editorial **ancestry mechanism** from direct N02-to-N06 lexical revision or concatenating fragments of other crew's captions.

I extracted 20 authentic original mail **bodies**, removed an explicit fixed list of common stopwords, and ranked every mail by the sum of `log(21/(mail_document_frequency(word)+1))` over exact remaining word overlap with each Emily note after its heading colon. This is deliberately simple, source-only and *retrospective*, not an independent blind language model.

| Emily note | Highest-scoring original mail donor | Score | Exact shared content tokens | Next-best score |
| --- | --- | ---: | --- | ---: |
| N02 first draft | MAIL-11 (Emily) | 3.44999 | next,room,watch | 2.35138 |
| **N06 second draft** | **MAIL-12 (Zoey)** | **5.73237** | **corridor,lamp,little** | 1.94591 |
| **N13 night recollection** | **MAIL-12 (Zoey)** | **8.82568** | **lamp,little,mugs,night,window** | 5.22154 |
| N20 editorial intention | MAIL-11 (Emily) | 9.79076 | because,label,line,night,standby,wanted | 7.03392 |

Independent heldout-style contextual point: selecting MAIL-12 from **N06** overlap also yields the top-ranked MAIL-12 for separate **N13**. The N13 ranking is retrospective because all sources were present at hypothesis selection, so it cannot be treated as a prospectively authenticated causal parent. Original N06/N13 lines are **undated**. MAIL-12's calendar date does **not prove** either Emily line was written afterward, and common subject matter is not evidence of copying.

The smaller source-context insight is that even very different complete Emily drafts may arise from **different external scene reports**. A global small-edit hypothesis connecting first to second directly is not the only plausible drafting path. This complements the v1 heldout vocabulary limit and does not reverse it.

## Direct original K08 complete-caption mechanism

An exploratory **complete-sentence semantic rewrite** was then generated from: MAIL-12's lamp/mug/window/corridor facts; N01/N08 sea imagery; and Emily's N20 and MAIL-11 end-of-night and communal-table intentions. This is distinct from v2 Agent2's **P+G+E contiguous source-span collage**, Agent3's source-preserving **two interior edits**, Agent21's source-agnostic four-role time/sea/room/people grammar, and the direct N13/N02/N06 base editing models. The new basis explicitly includes independently dated MAIL-12 and allows novel predicative wording instead of inheriting complete source fragments.

A fixed finite family of **20 lamp/mug scene predicates × 18 sea predicates × 18 temporal clauses × 20 communal-table predicates × six complete-sentence layouts** produced exactly **777,600 full normalized phrases**. The unmodified original desk nonce `5F933DA6A1BD03C32DA5CBC25344F497` gives HMAC-SHA256 first16; its full component SHA256 is compared with the unchanged original K08 slot digest `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

**Original result: NO_MATCH, 0 / 777,600.** The original N02 draft HMAC independently reproduced known `BF889359B0303F2B2B2FD96AE841210B`; one planted full sentence returned exactly one synthetic hit. Exact original crew-note SHA-256 was asserted (`13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`). Original source, acceptance and candidate were read only.

Local complete executable probes:
- `h17_k08_mail12_lineage_sft.py` SHA256 `6237447ccbd7430d9e15331ca470631a4b9270b93ba6a07dd443aae5637d03d5`;
- `h17_k08_mail12_full_rewrite.py` SHA256 `c5db60d03d4f7dc74da0a7770442a7dface706e879c135e873741e9deac1173e`.
Both were run read-only on the original 46-file ZIP extracted to the local root.

## Research implications and limitations

No original final-caption word can be inferred obligatorily from this source relationship. MAIL-12 has no provenance link to the missing N23 envelope. The 777,600 search excludes its precise full-phrase grammar only; the final could omit the lamp or all these literal motifs. The **stronger potential next mechanism** is a historically sourced cross-author creative rewrite with an actual terminal witness or a genuinely blind independently calibrated source-to-author generator, rather than expanding 20×18 motif grids automatically.

**REC8 state:** six verified slots PASS, K04/K08 MISSING, combined INCOMPLETE. Original target recovered information remains 0 authenticated selected K04 bits and 0 attested final K08 words.
