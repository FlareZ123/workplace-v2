# K08: internal complete literary passages from source-linked Noyes works

**Agent 18 | 7 November 2026 | genuine original K08 NO_MATCH in 7,120,418 distinct complete phrases.**

## Why this was a different test

[Agent25's same-day source-linked result](h17-k08-noyes-literary-name-link-20261107.md) tested **complete printed lines, 2-3 printed-line groups and whole prose sentences** from three Alfred Noyes books. The surname of the company, the tea/sea photograph theme and MAIL09's unidentified map-bearing library book made that literal quotation source a weak, conditional historical possibility. Agent25 found no match among 94,619 whole-line/sentence candidates. Agent25 expressly regarded the relationship as unproven.

The remaining *specific* literary-copy hypothesis was a keeper's margin that copied **a short, intact substring from the middle of a printed sentence or paragraph**, rather than a complete printed line or whole sentence. The test below covers that distinct representation without adding new books, changing words or generating paraphrases. It does not claim the original source identifies any title or confirms that Emily read Noyes.

## Method

The [source-pinned standard-library runner](../agents/agent18/k08_noyes_internal_passage_sft.py) reuses Agent25's exact public Gutenberg downloading/parsing, pins all three downloaded original raw SHA256 digests and original crew notes SHA256, and first checks the known actual N02 HMAC16 reference. A synthetic genuine subparagraph planted-window control must pass.

For each Gutenberg plaintext, tokenize each paragraph as normalized ASCII-alphanumeric words; enumerate all contiguous complete **4..28-word windows within a paragraph**, deduplicating separately within each book. For every candidate use the *original* K08 transformation: decoded desk nonce as HMAC-SHA256 key, normalized UTF-8 phrase as message, first 16 digest bytes as component, and full SHA256 against unchanged K08 commitment. No arbitrary word replacements, reordering, deletions within the window, or metadata-only lookup are included.

## Executed original results

[Manual-only Actions run 42336708188](https://github.com/FlareZ123/workplace-v2/actions/runs/42336708188), head \`d176b54f15cfb4f9288014610fbb9ce635ffde0b\`, completed SUCCESS 7 November 2026 04:03:58 UTC. All original-source and planted-subparagraph controls PASS. Its actual job log reports:

| Gutenberg work | Book ID | Distinct normalized complete phrases | Full original K08 matches |
| --- | --- | ---: | ---: |
| Collected Poems, Volume One | 30501 | 2,815,771 | 0 |
| Collected Poems, Volume Two | 30599 | 2,697,056 | 0 |
| Walking Shadows: Sea Tales and Others | 43186 | 1,607,591 | 0 |
| **Total** | | **7,120,418** | **0** |

The complete original source identity is pinned to the three independent hashes in the runner, matching Agent25's original archive acquisition report. The [manual workflow](../.github/workflows/agent18-k08-noyes-passage-manual.yml) does not run automatically on each commit. Its only external traffic is ordinary public Project Gutenberg text acquisition. No external source body was added to the repository.

## Meaning

There is **no accepted K08 component** among these 7.12 million complete literal internal passages. This closes just the frozen 4..28-word contiguous-paragraph-copy hypothesis in these three exact public works. It does not exclude other books, Emily's original wording, a longer/much shorter quotation, an edited quotation or an authentic original final margin. The hypothesized company-name literary connection is weak and should not drive another open-ended corpus sweep.

K04's original selected physical coupon remains absent; K08's exact chosen final words remain unknown. Six established slots PASS; combined REC8/1 remains INCOMPLETE. Original files, K08 acceptance, official verifier and candidate state were not edited.
