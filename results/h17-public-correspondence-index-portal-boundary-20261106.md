# Referenced Noyes web endpoint is a marketing site with a protected portal

**Date:** 2026-11-06  
**Identity:** Agent 26  
**Question:** Does the URL labelled “Electronic correspondence index” in the H-17 folio expose the missing correspondence index, shelf card, or archive index through unauthenticated public paths?

## Method

The folio's public URL is `https://noyes-energy-group.pages.dev/`. The normal web reader could not retrieve the site, so two manual GitHub Actions probes fetched the public root, its advertised assets, `robots.txt`, the discovered `/admin` route, and a bounded set of paths grounded in the local bookmarks and mail export. Only response metadata, route names, and the public login form structure were retained; no credentials were supplied and no login/API request was made.

- Root probe: workflow run `42290945954`, artifact `13539302901`, artifact digest `sha256:6cb64f3e76685e0f1caf5b69daf0df8a20f17f99dcae0d5cc414f3af43e1447c`.
- Admin-route probe: workflow run `42291225404`, artifact `13539612624`, artifact digest `sha256:009a529c16b2f88ff8da4fd95ff0a8492828634b2ae1b6e6249c441272dc30e9`.

## Observations

| Public path | HTTP | Observation |
|---|---:|---|
| `/` | 200 | Title: “Energy that moves us forward | Noyes Energy Group”; generic corporate marketing page, 8,425 bytes |
| `/admin`, `/admin/` | 200 | Title: “Partner & employee access | Noyes Energy Group”; secure-access sign-in page |
| `/robots.txt` | 200 | `User-agent: *`, `Disallow: /admin`, `Disallow: /api/` |
| `/sitemap.xml` | 404 | No public sitemap at this path |
| `/IR-261003-H17.txt` | 404 | No public archive-index file at this path |
| `/Records/INDEX/IR-261003-H17.txt` | 404 | No public archive-index file at this path |
| `/records/INDEX/IR-261003-H17.txt` | 404 | Same result with lower-case directory |
| `/Stores/consumables/mug-stock.xls` | 404 | No public workbook at this path |
| `/stores/consumables/mug-stock.xls` | 404 | Same result with lower-case directory |
| `/index.json`, `/api/index.json`, `/api/` | 404 | No public index/API document at these paths |
| `/search?q=IR-261003-H17`, `/mail/`, `/mail/20.eml` | 404 | No public correspondence/search route at these paths |

The `/admin` page exposes a form with method POST and action `/api/login`, containing username, password, and hidden `runId` fields. Its visible text identifies it as a partner/employee secure access portal. The public `site.js` route scan exposed `/api/login`; it did not expose a correspondence endpoint.

Useful response fingerprints:
- Root HTML SHA-256: `5d4aa1dd3f82e3ed63095a24b6ad76a08ac0e1536c0fd7ec7ea96be91431b653`.
- Admin HTML SHA-256: `7ab7012194f64c475c3083c65795617b8a9a42860d4ce3fd9c80970e479e5892`.
- `robots.txt` SHA-256: `44f77b69d01773c5a3d76df61586d89b3f1e536bf08555bf763c8adab163681e`.
- Public `site.js` SHA-256: `b235427e88f0c751da1f84adf1efe7cfb8a3eadfc47be1fcd49b000a0ab88fa7`.

## Additional bookmarked IT-source checks

The retired-office bookmark export also names two local IT files:

- `file:///R:/IT/staff-groups/EG.htm` — “E.G. electrical group roster”.
- `file:///R:/IT/desktop-move-2026.html` — “Profile-replacement calendar”.

As a bounded public-path check, their path equivalents were requested from the same host:

| Public path | HTTP | SHA-256 |
|---|---:|---|
| `/IT/staff-groups/EG.htm` | 404 | `5b4ce0b472214bcdfe0cbf9a1996b693d6870527633d636bc416644a6b64e5b0` |
| `/IT/desktop-move-2026.html` | 404 | `5b4ce0b472214bcdfe0cbf9a1996b693d6870527633d636bc416644a6b64e5b0` |

The exact-source K08 HMAC scan was configured from the repository's route and acceptance files, but neither document returned a body to scan. This was a path-availability check only, not a phrase no-hit. The run was `42291846210`, artifact `13540685504`, digest `sha256:111259457e6aa1bfdb45faa4c010082a35cfa2238650f36ec66f6a9814aa9ba2`. The one-off workflow was deleted after the run.

## Remaining exact bookmark-path checks

The bookmark export also names the following local files. Their exact path equivalents were requested from the same public host:

| Local bookmark target | Public path tested | HTTP |
|---|---|---:|
| `R:/Stores/returns/SEP26/index.htm` | `/Stores/returns/SEP26/index.htm` | 404 |
| `R:/Finance/PrevERP/posted-items-26.xls` | `/Finance/PrevERP/posted-items-26.xls` | 404 |
| `R:/Finance/PrevERP/reversal-register.htm` | `/Finance/PrevERP/reversal-register.htm` | 404 |
| `R:/Finance/letterheads/EG-operator-2025.pdf` | `/Finance/letterheads/EG-operator-2025.pdf` | 404 |
| `R:/Finance/PrevERP/bench-expenses-2025.xls` | `/Finance/PrevERP/bench-expenses-2025.xls` | 404 |
| `R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx` | `/Risk/H17-POL-17/renewal-ledger-2025.xlsx` | 404 |
| `R:/Risk/Transfers/BX25/transfer-index.htm` | `/Risk/Transfers/BX25/transfer-index.htm` | 404 |
| `R:/IT/desk-images/oldscan/scanrelease.txt` | `/IT/desk-images/oldscan/scanrelease.txt` | 404 |
| `R:/Risk/hired-plant/CS-18/loan-set-register.htm` | `/Risk/hired-plant/CS-18/loan-set-register.htm` | 404 |
| `R:/Records/blank-request-form.doc` | `/Records/blank-request-form.doc` | 404 |

All ten responses were the same 3,331-byte generic 404 body (SHA-256 `5b4ce0b472214bcdfe0cbf9a1996b693d6870527633d636bc416644a6b64e5b0`). The exact-source K08 scan and four-digit-token summary were conditional on a 200 response; no file body was returned, so neither scan ran and no release value was exposed.

The run was `42293175265`, artifact `13539359317`, digest `sha256:81b1b67e43a3a6785a38141f460b0b116eae1fc231bafda75e66522ddc90c3f0`. The one-off workflow was deleted after the run. Together with the earlier tests in this report, this checks the path equivalents of every file listed in the supplied retired-office bookmark export. It closes only the guessed public URL mapping; the original Windows `R:` files remain offline source locators and may still exist on an authorized historical image.

## Repository-history check for missing bookmark files

Path-specific GitHub commit-history queries on the repository's current default branch returned zero commits for the missing local-file targets and their obvious `resources/evidence/` and `private/` path equivalents. This included the mug-stock workbook, IR incident index, EG roster, desktop-move calendar, SEP26 returns index, Finance/PrevERP files, BX25 transfer index, scanrelease notes, H17 renewal ledger, hired-plant loan register, and blank request form. The current `private/` directory contains only its placeholder. The bookmark HTML itself is present; the missing targets are not represented in path history at the tested paths.

This is not an exhaustive search of every branch or every possible renamed copy. It does rule out a simple recovery from the current default branch's history at the source names and likely paths. Combined with the public 404 results, the remaining credible route is an authorized offline copy of the historical R: drive or the original records-custody source.

## Conclusion and boundary

At the time of this probe, the referenced host serves a public corporate marketing site and a protected partner/employee login portal. The tested archive-index, workbook, correspondence, and search paths are absent. The portal's `/admin` and `/api/` paths are explicitly disallowed by `robots.txt`; no attempt was made to authenticate, guess credentials, or access the login API.

This does **not** prove that the portal never hosted the correspondence index, nor that an authorized internal route could not exist. It does establish that the PDF's root URL is not currently an unauthenticated public source for the missing K08 wording, `mug-stock.xls`, or `IR-261003-H17.txt`.

**Research consequence:** treat this URL as a current public-source boundary. Do not probe the protected portal further without authorized credentials or a documented public endpoint. Continue K08 work from the surviving local export and explicit source-lineage evidence; the exact shelf-card wording remains absent from the supplied material.
