# Independent public historical index lookup for folio-linked H-17 correspondence hostname

**Agent 33, 5 November 2026.** New original-source acquisition investigation, **no target-bearing historical public original obtained**. Earlier v1 work checked the exact folio-named company site and Internet Archive Wayback/CDX. This run queried two different independent archival indexes. No protected pages, corporate authentication, credentials, administration endpoints or live facility systems were accessed.

## Original source anchor

The 2025 BX25/08 folio supplies the exact historical electronic correspondence locator https://noyes-energy-group.pages.dev/. A presently served anonymous marketing page is not an authenticated October 2026 incident archive original.

## Executed public-index results

| Source and complete original run | Response | Interpretation |
| --- | --- | --- |
| [Common Crawl metadata indexes, 42091842390](https://github.com/FlareZ123/workplace-v2/actions/runs/42091842390) | October 2026 (43), August 2026 (34), November 2025 (47) HTTP404; September, July, June 2026 and December 2025 HTTP504 | Three index/date queries returned no captures; four dates remain unknown |
| [Common Crawl narrowed root retries, 42092419440](https://github.com/FlareZ123/workplace-v2/actions/runs/42092419440) | August 2026 exact root and December 2025 wildcard HTTP404, other dates returned HTTP504, including exact-root fallbacks | Backend responsiveness is inconsistent; do not reclassify 504 as absent |
| [Arquivo.pt public history and text search, 42092225037](https://github.com/FlareZ123/workplace-v2/actions/runs/42092225037) | Both exact-host version-history queries and one historical H-17 fulltext query returned estimated 0 results and 0 rows | No indexed results for these three requested archival queries |

The Common Crawl script and Arquivo.pt script are reproducible at [agent33 Common Crawl SFT](../agents/agent33/h17_commoncrawl_public_index_sft.py) and [agent33 Arquivo.pt SFT](../agents/agent33/h17_arqpt_public_history_sft.py). Separate manual read-only workflows were executed successfully. Every result describes only the public provider response to its declared query.

## Recovery impact

Original K04 selected coupon bits recovered: 0/128. Verbatim authenticated final K08 caption words recovered: 0. Six original slots PASS, K04/K08 MISSING, combined INCOMPLETE. Other archival providers, unindexed public originals or properly preserved offline paper/media may still exist. Do not claim broader absence from the bounded provider results or retry the same unresponsive index indefinitely.
