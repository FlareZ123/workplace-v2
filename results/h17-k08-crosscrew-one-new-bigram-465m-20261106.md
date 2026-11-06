# K08: cross-crew one-novel-bigram editor, 465,489,177 complete original-source captions

**Agent 2 | 6 November 2026 | Original unchanged K08 commitment NO_MATCH | all ten independent manual CI partitions SUCCESS.**

## New mechanism beyond Emily-only editor

Original MAIL-11 says Emily developed final keeper-envelope wording using **desk notes and photograph captions**. The 24 original N01..N24 crew-note bodies contain Jason's bench/sea/window, Zoey's galley cup/night, David's mug, Gabriel's sunrise/boat and Emily's own drafts and explanatory reflections. The earlier [Emily-only exactly-one-novel-bigram search](h17-k08-emily-one-new-bigram-692m-20261106.md) included only eight Emily notes and their 90 words/130 adjacent pairs. This independent extension tests all **24 crew authors' surviving note lines** as the source of adjacent word pairs, with one new editorial transition. It is distinct from previously exhausted all-attested source-bigram walks because it explicitly permits **one** missing directed edge.

The source cue supports cross-crew photograph influence but gives no literal terminal text, no number of changes, and no authenticated final text ancestor. Therefore this is a conditional candidate-family falsifier, **not** evidence that the final inscription was a one-edit collage.

## Exact candidate family and frozen original inputs

Read original unchanged `resources/evidence/crew/noticeboard-and-desk-notes.txt` SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. Parse and assert all 24 note IDs N01..N24, consume their literal note-body line tokens as ASCII alphanumeric lowercase. This gives exactly **222 distinct word types** (newline-sorted SHA256 `e5c52e87e6011a4f6b0f3317ec243a82d24a6d2cf7f131a2f8eb9c80e58556e0`) and **348 distinct directed observed word-pair edges**.

Enumerate complete normalized word sequences of length **6–12 inclusive** with exactly **one** adjacent pair absent from those 348 original edges and *all remaining* adjacent pairs attested in at least one of the 24 notes. Permit starts and ends at any historical word, repeats, source changes between records and new edge anywhere. No fixed passage, syntactic order or word-frequency filter.

Apply only the three independently text-motivated content groups from N20, one word anywhere from each: `{sea,water}`, `{night,watch,morning}`, `{room,voices,table,people}`. Every candidate is already lowercase single-space normalized, matching original acceptance normalization. Distinct sequence corresponds to exactly one graph word walk, so no double counts within the family.

The unchanged original K08 exact reduction is `SHA256(HMAC_SHA256(hex_nonce, UTF8(normalized_caption))[:16])`, where nonce `5F933DA6A1BD03C32DA5CBC25344F497` and full target `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. Original K08 commitment, checker, candidate and source were read-only.

## Independent finite coverage calculation

Before original search, a separately implemented Python dynamic program over all 222 words, their original 348 edges, three motif flags, new-edge-once flag, and lengths6..12 determined the exact number of distinct eligible complete strings:

| Complete phrase words | Distinct normalized captions |
| ---: | ---: |
| 6 | 7,465 |
| 7 | 51,168 |
| 8 | 417,157 |
| 9 | 2,522,538 |
| 10 | 13,900,342 |
| 11 | 75,145,848 |
| 12 | 373,444,659 |
| **Total** | **465,489,177** |

This count was also partitioned by **first word index**, with expected shard cardinalities frozen into the independent C++17/OpenSSL enumerator. The sorted source vocabulary is split into nine equal 23-word first-index ranges and final 15-word range.

## Completed original GitHub Actions search

[Exact source-pinned C++ reproducer](../agents/agent2/k08_crosscrew_single_new_bigram_sft.cpp), [manual-only parallel workflow](../.github/workflows/agent2-k08-crosscrew-one-bridge-manual.yml), [completed run 42291033349](https://github.com/FlareZ123/workplace-v2/actions/runs/42291033349) on 6 November 2026, all **ten independent jobs SUCCESS**. Every job log was retrieved via the GitHub Actions job-log interface and checked for exact expected candidate count, zero original matches and its own positive control.

Each original source job checks known historical complete N02 HMAC16 `BF889359B0303F2B2B2FD96AE841210B`. Prior to the run, ten different complete 12-word legal graph paths were independently generated in Python, exact original HMAC/SHA256 hashed, and fixed into the C++ job as per-shard planted full-caption positives. Every shard finds the planted text **exactly once** under a separate synthetic target commitment. These are synthetic controls only; their text may be stylistically odd because the graph has no sentence grammar, which illustrates the conditional family limitations.

| First word indices | Original complete tested | Genuine K08 matches | Full planted positives |
| --- | ---: | ---: | ---: |
| 0..22 | 53,755,096 | 0 | 1 |
| 23..45 | 33,264,636 | 0 | 1 |
| 46..68 | 46,667,100 | 0 | 1 |
| 69..91 | 30,404,323 | 0 | 1 |
| 92..114 | 40,301,026 | 0 | 1 |
| 115..137 | 58,085,699 | 0 | 1 |
| 138..160 | 29,118,741 | 0 | 1 |
| 161..183 | 62,433,738 | 0 | 1 |
| 184..206 | 95,448,170 | 0 | 1 |
| 207..221 | 16,010,648 | 0 | 1 |
| **Total** | **465,489,177** | **0** | **10** |

The successful original run source checkout SHA was `0e5826a2c617741bd5510de07ef5c1aee3b44d42`. Every job asserted the original evidence SHA, exactly 24 original note IDs, 222 unique word types and 348 exact original edges. CI success reflects successful exhaustive execution, not a seventh or eighth accepted key slot.

## Interpretation, limits and remaining target

This closes **all** complete six-to-twelve-word source paths over all crew-note word types, with exactly one newly authored bigram and the three historic motifs. It does **not** exclude a final phrase requiring two or more invented transitions, thirteen-plus words, absent motif word, words outside surviving notes, or some alternative authorial operation. Do not grow this exact source graph blindly to astronomically many longer strings without a historical version witness.

The original final margin is still unquoted and K08's component is not recovered. K04's independent physical coupon remains unobserved. Six original REC8 components (K01,K02,K03,K05,K06,K07) remain individually PASS, K04/K08 MISSING, combined INCOMPLETE.
