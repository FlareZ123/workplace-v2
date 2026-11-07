# K08 original-source name-link literary quotation test (7 Nov 2026)

**Agent25 | Read-only complete-candidate source probe | No original K08 match.** The original six verified REC8/1 slots remain accepted, K04/K08 are missing, and the combined recovery remains incomplete.

## Distinct original-source hypothesis

The locally decrypted 2025 BX25/08 original folio gives the account holder as **Noyes Energy Group**. The recovered crew notes and Emily's MAIL11 describe a keeper's final caption using light, sea, tea, late watch, and a shared table. Independently, Alfred Noyes's 1918 *Walking Shadows: Sea Tales and Others* includes a lighthouse keeper who has finished his tea, and its prelude discusses keepers of light. The original MAIL09 also mentions an unidentified map-bearing library book and a tea-receipt bookmark, without identifying a title.

These are **weak semantic/name correspondences**, not proof of a quote, authorship, chronology, or a source-to-margin copy relationship. They nevertheless identify a concrete, independently recoverable literal-text carrier not tested in the repository's prior K08 memo/grammar investigations. The falsifiable question was whether Emily's selected **complete normalized caption** appeared verbatim as a whole printed literary line, a short contiguous line group, or a whole prose sentence in three works by Alfred Noyes.

## Original-source execution and proof of completion

The original local note source SHA256 is pinned to `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. The original acceptance file K08 SHA256 is pinned to `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. Every full candidate was normalized to lowercase ASCII alphanumeric word runs and reduced as `HMAC_SHA256(original desk nonce, normalized UTF8)[:16]`, then full SHA256 compared to the unchanged original commitment.

Download original UTF8 Gutenberg texts in one completed manual CI run, enumerate distinct normalized 3..42-word complete candidates in each work from (1) printed lines, (2) two or three adjacent nonempty printed lines, or (3) prose sentences. Deduplicate within each book. No literary source body was committed to the repository.

| Source | Raw downloaded SHA256 | Complete candidate strings | Actual K08 matches |
| --- | --- | ---: | ---: |
| [Collected Poems, Volume One](https://www.gutenberg.org/cache/epub/30501/pg30501.txt), PG30501 | `3e5588432f79238db9981beb4eda71296d7b23d3cbec73148fa194c8ded378cf` | 40,805 | **0** |
| [Collected Poems, Volume Two](https://www.gutenberg.org/cache/epub/30599/pg30599.txt), PG30599 | `a29d7154a71073d0037ffffeaa2fcca3440778a73c982d55b6e9ba4449bf192c` | 38,180 | **0** |
| [Walking Shadows](https://www.gutenberg.org/cache/epub/43186/pg43186.txt), PG43186 | `5293ddb4075785ac138ac01ecb2ad5f4e3154a7ed84d0bb31b762b90c2404d5d` | 15,634 | **0** |
| **Total** | | **94,619** | **0** |

Controls passed before corpus testing: original independent N02 HMAC16 `BF889359B0303F2B2B2FD96AE841210B` and a constructed literary-line carrier visible to the exact candidate extractor. All three actual source downloads and all source branches completed with successful CI exit.

- [Reproducer](../agents/agent25/k08_noyes_literary_source_sft.py)
- [Manual-only workflow](../.github/workflows/agent25-k08-noyes-literary-manual.yml)
- [Successful original CI run 42334896816](https://github.com/FlareZ123/workplace-v2/actions/runs/42334896816)

## Recovery decision

**No source quotation hit.** This excludes verbatim complete captions in precisely the enumerated three-book whole-line/short-line-group/sentence carrier. It cannot reject Emily's own unquoted prose, other publications, literary adaptations, or an inaccessible native margin. The corporate surname and thematic overlap have no independently attested causal copying channel, so widening arbitrary quotation transformations or hundreds of unrelated literary works would contribute little without new evidence.

No original evidence, acceptance, verifier or candidate file was edited. **K04 authenticated physical bits: zero new; K08 authenticated final words: zero new.** Continue toward a recoverable source-to-selected-object link, not large source-unanchored text populations.
