# H-17 K08: long scene-source graph and one-edit anchor trials (16 November 2026)

**Agent 7. Historical K08 acceptance: no match in completed domains.** These are complete-phrase experiments from conditional source-derived authoring rules. They do not supply a seventh accepted component or authenticate the final envelope sentence.

## Source and exact reduction

Unmodified original export from `h17-archive-dump.zip`: 24 N01–N24 note bodies and MAIL11/MAIL20 bodies, omitting the two prior-envelope quotation strings from the email copies as in Agent45/Agent1's shared graph convention. Lowercase ASCII alphanumeric words; construct one directed bigram for each consecutive pair within a source record, deduplicate edges, permit cross-record joins at shared words. Source graph: **26 records, 331 words, 570 directed edges**. All four executed C++17/OpenSSL runners pin the three source SHA256s: notes `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`; MAIL11 `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`; MAIL20 `e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71`.

Every complete phrase is tested against the **original** immutable target `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747` using `SHA256(HMAC_SHA256(raw 16-byte nonce, UTF8(normalized phrase))[:16])`, nonce `5F933DA6A1BD03C32DA5CBC25344F497`. The known original N02 HMAC16 `BF889359B0303F2B2B2FD96AE841210B` was independently reproduced in Python. Source graph and commitment were never edited.

## Newly tested complete candidate families

| Complete authoring/copy model | Lengths | Full authentic-target comparisons | K08 hits | Planted in-domain controls |
| --- | ---: | ---: | ---: | --- |
| All source-bigram paths containing literal sea/water, night/watch/morning and table/voices/room motifs | 15 | 1,018,097,847 | 0 | 1 of 1 |
| Source-bigram paths whose three motif groups occur in sea → night → table **block order** | 16 | 1,053,467,125 | 0 | 1 of 1 |
| Same strict motif-block order | 17 | 5,243,475,873 | 0 | 1 of 1 |
| Source-bigram paths with a sea/water word, then the intact consecutive words `at the end of the night`, then the intact words `voices at the table`, in that order; intervening ordinary source words permitted | 16–25 | 303,122,409 | 0 | 10 of 10 |
| Exactly one *unattested* directed adjacent-word transition among the same 331 source words, all other bigrams attested, plus those same two ordered intact phrases after sea/water | 14–21 | 264,919,776 | 0 | 6 of 6 (lengths 16–21); lengths 14–15 count-only |

The **7,883,083,030** checks summed across the five table rows are execution counts across overlapping models.

Expected counts were independently calculated by a Python dynamic-programming oracle over word ID, motif/anchor progression, and, for the final model, the one-new-edge flag. Each executed band independently checked its exact prescribed full-path count; the C++ runners reproduced each reported expected count. Synthetic positives were precomputed with independent Python `hmac` and `hashlib` before original-target comparison. The two one-new-edge length14/15 bands have 212 and 2,256 complete original checks, respectively, with exact count assertions; their planted target remains deliberately inactive. All other listed bands recovered their synthetic full phrase exactly once.

**These tested sets overlap.** An aggregate check count is an execution total, not the cardinality of a disjoint global vocabulary or proof the final author used any hypothesized model. The fully attested bigram graph and one-novel-bigram model are conditional editorial mechanisms, not source-dated evidence of Emily's actual final revision. Most graph walks are not grammatical sentences.

## Reproduction and next decision

Portable C++17/OpenSSL/OpenMP source:

- [`agents/agent7/k08_motif15_sft.cpp`](../agents/agent7/k08_motif15_sft.cpp): exact 15-word three-motif corpus walk.
- [`agents/agent7/k08_ordered16_17_sft.cpp`](../agents/agent7/k08_ordered16_17_sft.cpp): strict scene-order 16/17 words.
- [`agents/agent7/k08_exact_anchors_sft.cpp`](../agents/agent7/k08_exact_anchors_sft.cpp): whole-clause anchor lengths 16–25.
- [`agents/agent7/k08_one_new_anchored_sft.cpp`](../agents/agent7/k08_one_new_anchored_sft.cpp): exactly one new bigram, anchor lengths 14–21.

Use the original `resources/` directory as `ROOT`, so the runner finds `ROOT/evidence/...`. The experiments were executed against exact ZIP-extracted source copies, with C++ OpenSSL HMAC/SHA256 and source checks, and did not modify official evidence, acceptance, verifier, or canonical `candidate.json`. The exact N20/Mail11 semantic intent is a search motivation only. A different full original/copy-stage mechanism, or authenticated final margin, is needed for further recovery. K04 remains unresolved; the six accepted slots remain unchanged and combined REC8/1 is incomplete.
