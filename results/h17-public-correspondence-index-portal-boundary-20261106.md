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

## Conclusion and boundary

At the time of this probe, the referenced host serves a public corporate marketing site and a protected partner/employee login portal. The tested archive-index, workbook, correspondence, and search paths are absent. The portal's `/admin` and `/api/` paths are explicitly disallowed by `robots.txt`; no attempt was made to authenticate, guess credentials, or access the login API.

This does **not** prove that the portal never hosted the correspondence index, nor that an authorized internal route could not exist. It does establish that the PDF's root URL is not currently an unauthenticated public source for the missing K08 wording, `mug-stock.xls`, or `IR-261003-H17.txt`.

**Research consequence:** treat this URL as a current public-source boundary. Do not probe the protected portal further without authorized credentials or a documented public endpoint. Continue K08 work from the surviving local export and explicit source-lineage evidence; the exact shelf-card wording remains absent from the supplied material.
