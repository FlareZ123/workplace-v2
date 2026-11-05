# K08: 2.135 billion source-ordered compressed phrases with one inserted source word

**Agent 10 | 5 November 2026 | Original K08 NO_MATCH.** All six previously verified REC8/1 slots remain PASS, the physical K04 coupon and Emily's exact K08 final margin remain MISSING, combined archive commitment INCOMPLETE. This is a complete-target cryptographic test of a **specific editorial construction**, not a claim that the missing final words have been inferred.

## New candidate mechanism and nearest prior art

Original note N23 is explicitly about Emily's **final margin**: “The wording in my margin was never an official slogan. The envelope only remembers the words I finally put on it.” Original N20 articulates her three scene themes; MAIL11 supplies an independent editorial description “people making room for each other after a long watch, with the water outside and the night almost finished.” N02 and N06 are authentic earlier Emily drafts.

A candidate final line could have arisen by **deleting many source words while retaining order and then inserting exactly one topical word** from the surviving scene vocabulary, including insertion before the first or after the last retained word. This is a **different complete-caption class** from [Agent3's N23 deletion-only search](h17-k08-terminal-custody-n23-ordered-subsequence.md) (no inserted word), literal bigram-only paths (prohibit unseen adjacent words), and the short purpose-conditioned grammars. The editorial operation is *not historically attested*. The phrases may differ from actual author's wording in arbitrarily many other ways.

The 91-word fixed lexicon comes from the already committed [Agent10 candidate construction](../agents/agent10/k08_author_source_compaction_insertion_sft.cpp), prepared on 4 November but **not previously accompanied by an executed original-target report**. Its vocabulary was investigator-curated after the visible earlier labels and descriptions; no independent blind prediction is claimed. This run completed **10** of that file's 11 frozen base phrases. The very long N13 22-word original was deliberately **not** searched; it would require another 3,086,541,640 full checks under the same model with weak source justification.

## Frozen complete-candidate grammar

For each of the 10 source-associated base word sequences, select any ordered subset of **4 through 12** words; preserve original word order; insert exactly one from the **91-word source lexicon** at any of 1..13 possible gaps. Normalize as lowercase single-space ASCII words without punctuation, then apply the exact original K08 HMAC-SHA256(key=16 raw desk-nonce bytes, message=the entire candidate UTF-8 text), truncate to first 16 digest bytes, and SHA256 those 16 bytes. Compare the **entire 32-byte result** with the unchanged K08 slot acceptance SHA256 \`285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747\`. Distinct deletion assignments can produce the same normalized phrase because the original contains repeated words; all numbers below are **complete assignment counts**, not claims of globally distinct texts.

Exact original inputs:
- Crew notes SHA256 \`13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb\`, author N02/N06/N23 original source words and N20 scene triad.
- MAIL11 SHA256 \`f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29\`, the full 19-word “people making room...” description.
- Original acceptance SHA256 \`681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f\`.
- Original K08 nonce \`5F933DA6A1BD03C32DA5CBC25344F497\`. First authentic N02 HMAC16 calibration \`BF889359B0303F2B2B2FD96AE841210B\`.

## Completed original-source K08 computation

| Base and editing source | Base words | Complete K08 assignments | K08 acceptance matches |
|---|---:|---:|---:|
| N02 first Emily draft | 13 | **5,461,911** | **0** |
| N06 second Emily draft | 11 | **1,134,224** | **0** |
| N20 motifs, all six fixed scene-order compactors | 13 each | **32,771,466** (six × 5,461,911) | **0** |
| MAIL11 19-word scene description | 19 | **442,658,580** | **0** |
| N23 final-margin meta-remark | 21 | **1,653,140,125** | **0** |
| **Total, 10 bases** | | **2,135,166,306** | **0** |

**Executed shard details, N23:** four disjoint source-mask ranges \`[0,524288)\`, \`[524288,1048576)\`, \`[1048576,1572864)\`, \`[1572864,2097152)\`; exact original full checks respectively **442,658,580 / 422,524,375 / 422,524,375 / 365,432,795**. All four **0 original matches**. Total **1,653,140,125**. An independent synthetic target built from \`the wording in my margin sea\`, a genuine N23 first-five-word subset plus one lexicon insertion, appeared exactly once in the actual first shard, zero in the other three. Observed shard wall seconds **264.514 / 255.515 / 256.134 / 228.689**, simultaneous C++17/OpenSSL processes.

**Executed shard details, MAIL11:** four disjoint mask ranges of size 131,072; **108,837,638 / 112,822,710 / 112,822,710 / 108,175,522** full original comparisons, all zero. A complete planted first-four-word-plus-“sea” candidate was recovered once in the first shard.

N02/N06 each executed once over all 2^13 and 2^11 masks respectively, zero original K08 matches and **one** planted complete-phrase positive each. Six N20 motif orders each executed full 2^13 masks, **5,461,911** comparisons/order with no target hits. The original local pilot planted \`the sea the night room\`, which lay inside three of these six editorial grammars; these positive counts were respectively 2,4,6 while the other three layouts were legitimately outside that particular planted target. The updated remote reproducer now uses a **different in-grammar synthetic target per base** formed from its first four words followed by one inserted \`sea\`, with mandatory positive when the tested mask range contains \`0xF\`; this adjustment is a reproducibility improvement, not an additional original K08 match.

All tests use the unchanged 46-member original archived evidence (locally extracted in a read-only work directory), acceptance commitment and nonce. The original historical eight-key candidate, verifier and source contents were neither modified nor replaced.

## Reproducibility, decision and scope

- Committed [original-source single-file C++17/OpenSSL reproducer](../agents/agent10/k08_author_source_compaction_insertion_sft.cpp) supports all eleven bases, arbitrary disjoint mask ranges, original source SHA pins, independently known N02 HMAC control, per-base full synthetic positive and complete original 256-bit digest comparisons.
- Local executed source-equivalent auxiliary C++ tests retained as \`h17_k08_n23_insert_sft.cpp\`, \`h17_k08_n20_insert_sft.cpp\`, \`h17_k08_drafts_insert_sft.cpp\`, and their disjoint shard outputs in the current invocation environment. The portable repository SFT was updated and read back; **a separate CI execution of that just-modified portable file is not claimed**.
- No claimed recovered author-final word follows from a negative hash check. The real K08 final phrase could paraphrase source material in novel words or have different edition history, length, deletion/insertion count, grammar, or motif order. N23 is a remark *about* her margin, not a historical assertion that she used any of its words in the inscription.
- Growing the same source-word insertion catalogue further, especially N13's unsupported 3-billion case, is not a demonstrated route to recovery. A new *source-authenticated final-version text carrier*, or a genuinely independent selection rule predictive on unseen original captions, is needed.

**K04 original coupon authentic bits: 0/128. K08 author-final authenticated words: 0. REC8/1 original combined status: INCOMPLETE.**
