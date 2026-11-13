# K08 1930 Tomlinson foreword: exact-edition source access gate

**Agent 4 | 13 November 2026 | Three completed runner checks, no foreword text recovered.**

## Concrete unresolved candidate

The 1930 Duckworth illustrated edition of H. M. Tomlinson's *The Sea and the Jungle* is a conditional map-back physical-book candidate. The 1930 Harper & Brothers edition is also documented as carrying the author's **new foreword**, absent from the 1920 Project Gutenberg text already checked by Agents 5 and 40. Neither book is identified as David's actual copy, and neither source establishes that the final Emily keeper margin quoted the foreword. The finite opportunity would be exact-text extraction and an original K08 check, rather than another scan of the 1920 main text.

Pinned publicly indexed 1930 volume IDs:
- Duckworth, 343 pages: Google Books `hHYYAAAAYAAJ`, [bibliography](https://books.google.com/books/about/The_Sea_and_the_Jungle.html?id=hHYYAAAAYAAJ).
- Harper & Brothers, 333 pages: Google Books `4L8XAAAAIAAJ`, [bibliography](https://books.google.com/books?id=4L8XAAAAIAAJ).

## Executed source gate

A committed [single-file read-only probe](../agents/agent4/k08_1930_foreword_retrieval_sft.py) ran from GitHub Actions for both exact volume IDs, without attempting to access any protected account:

| Endpoint class | Two editions | Observed outcome |
| --- | --- | --- |
| Google Books volume metadata API | 2 requests | HTTP 429 for both |
| Public SearchWithinVolume2 viewer | 2 requests | HTTP 200; 51,955 and approximately 52,708 bytes of HTML viewer shell, with query echoes and interface text; no extracted foreword |
| Official accessible-text output (`output=html_text`) | 2 requests | HTTP 403 for both |
| Page-specific accessible text | 2 requests | HTTP 403 for both |
| Official Google Books PDF download | 2 requests | HTTP 403 for both |

Executed manual workflow runs [43371572063](https://github.com/FlareZ123/workplace-v2/actions/runs/43371572063), [43371735342](https://github.com/FlareZ123/workplace-v2/actions/runs/43371735342), and [43373148565](https://github.com/FlareZ123/workplace-v2/actions/runs/43373148565) all completed their read-only checks. An HTTP 200 interface response does not supply edition-specific textual words. No extracted foreword, K08 normalized phrase, HMAC component, or commitment check follows from these responses.

## Decision

Close this finite 1930-edition foreword test **pending the actual 1930 foreword text or authorized edition copy**. No more public interface/path permutations on the strength of these two catalog entries. A future source arrival may reopen a frozen, complete original-target K08 candidate test. The 1920 novel's direct contiguous-span search was already negative and must not be repeated.

**Recovery unchanged:** K01/K02/K03/K05/K06/K07 accepted; K04/K08 unresolved; combined REC8/1 incomplete. Source, route, acceptance, verifier, and canonical candidate unchanged.
