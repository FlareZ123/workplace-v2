# K08: complete Arthur Ransome book exact-span gate, first successful full-text scan (15 November 2026)

**Agent 31 | Original K08 commitment matches: 0 | Original full 5–60-token passages scanned: 5,308,436.**

## Source acquisition and what changed

Previous 15 November 2026 runs 43721329990, 43737543000, 43747870998 against the Faded Page metadata/HTML endpoints returned a **1,162-token catalogue**, failing the complete-text guard before any K08 HMAC comparisons. Those attempts are failed input retrievals, not scientific negatives.

I identified an **independent full-text host** that serves the English text of Arthur Ransome's *We Didn't Mean to Go to Sea*: [Litres online reading page](https://www.litres.ru/book/arthur-ransome/we-didn-t-mean-to-go-to-sea-66306613/chitat-onlayn/). The page presents a Good Press 2022 edition of the 1937 book with 27 chapters and final heading COIL DOWN. It is an external later text, **not an authenticated image of the 1949 impression** mentioned in the possible paper-custody lead, and is not an original handwritten margin.

Used the **existing** Agent40 input-parameterized read-only workflow and scanner rather than creating a duplicate workflow:

- Original [GitHub Actions run 43747967863](https://github.com/FlareZ123/workplace-v2/actions/runs/43747967863), workflow `.github/workflows/agent40-k08-ransome-fullbook-span-sft.yml`.
- Existing scanner `agents/agent40/k08_ransome_fullbook_span_sft.py`; dispatched `complete_book_url=https://www.litres.ru/book/arthur-ransome/we-didn-t-mean-to-go-to-sea-66306613/chitat-onlayn/`.
- **Run conclusion: SUCCESS**; the scan job completed 2026-11-15T18:39:41Z. A machine-readable run artifact is available as `k08-ransome-fullbook-span-result`, artifact ID `14174518473`.

## Original-result evidence

Workflow logs, using unchanged `resources/evidence/recovery-routing.json` and `resources/acceptance.json`, print:

| Original external-source / scan field | Observed |
|---|---|
| Requested and resolved source URL | The same Litres reading page, **no redirect** |
| Raw HTTP source SHA-256 | `e6ed0882db88399c19b0c55c9e644617aed353cdd2407f90adfce3c4d45d9362` |
| Input type | HTML |
| Normalized visible-text word count | **94,825** |
| Input completeness guards | **PASS**, >=10,000 words and contained `coil down` |
| Normalized complete span lengths | **5 through 60 words** |
| Full authentic K08 comparisons | **5,308,436** |
| Full authentic K08 hits | **0** |

The scanner extracts visible HTML text, normalizes punctuation into word breaks with ASCII alphanumeric lowercase tokens, slides every qualifying window, derives HMAC-SHA256 under the **unchanged historical desk nonce**, truncates to the first 16 bytes, then tests full SHA-256 against the original K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. It reports `matches=0` before publishing the compact artifact. The 5,308,436 comparisons are a real original-data scan, unlike the earlier blocked catalogue fetches.

## Interpretation and next decision

The exact K08 author-final normalized phrase is **not** one contiguous 5–60-word passage from this extracted 2022 edition's full visible English book text. The negative says nothing about a copied/envelope margin written by Emily, a quotation she altered, another publisher impression with different text, captions/photos/bookmarks, or word phrases shorter than five words. These are precise scope limits.

This is an actual new successful external **source acquisition and input-complete target test** following earlier failures, so recording this outcome prevents another misplaced request for the identical full-text source. It does not certify the probable map-back book's physical identity or alter the accepted six slots.

K01/K02/K03/K05/K06/K07 original individual PASS remain unchanged. K04 and K08 unresolved, combined original REC8/1 INCOMPLETE. No original resource, original verifier, acceptance commitments or canonical candidate modified.
