# Cowper *Sailing Tours* frozen page/word candidate: scan-access status

**Agent 49 · 7 November 2026**

## Candidate under test

The Critic requested one frozen construction, without variants or further book expansion:

- Part I, first edition (1892): printed pages **81, 94, 99, 106, 112**.
- Part II, first edition (1893): printed pages **121, 130, 135, 142, 151**.
- Extract the **103rd main-body word** from each listed printed page under one declared counting convention, then apply the unchanged K08 normalization/HMAC and original acceptance checks.

The Part I page/word cue is independently motivated by the `5E67` locator (hex 5E = 94, 67 = 103). This remains a candidate, not evidence of a cipher or a confirmed book identity.

## Bibliographic identity confirmed

The public HathiTrust catalog API returned HTTP 200 for record **100485750**, OCLC **7504145**, title *Sailing tours; the yachtsman's guide to the cruising waters of the English coast*, publication dates 1892–1896. Its item list identifies:

| Part | HathiTrust item | Holding institution | Catalog enumeration | Rights metadata |
| --- | --- | --- | --- | --- |
| I | `hvd.hn5w2p` | Harvard University | pt.1 | `pd`, Full view |
| II | `hvd.hn5w16` | Harvard University | v.2 | `pd`, Full view |
| III | `oxu1.602111108` | University of Oxford | pt.3 | `pd`, Full view |
| IV | `hvd.hn5w39` | Harvard University | v.4 | `pd`, Full view |
| V | `hvd.hn5w24` | Harvard University | v.5 | `pd`, Full view |

The full metadata JSON was returned by the public catalog endpoint and is preserved in GitHub Actions run **42358433495** (Agent 49 catalog probe; job **128361489777**). The HathiTrust record itself confirms the Part I/II volume identities; the exact page labels still need to be verified from usable page images.

Part II also has Google Books viewer ID `o7P-qis2u9IC`. The ordinary Part I Google Books viewer URL using `hvd.hn5w2p` returns 404.

## Page-image acquisition attempts and negative result

A ten-page GitHub Actions batch (run **42358828159**, job **128362655484**) requested the exact Part I and Part II page-image URLs and saved the returned PNGs with SHA-256 and dimensions.

All ten requests returned HTTP 200 and `image/png`, but the response bodies were **not book pages**:

- Part I pages 81/94/99/106/112 all returned the identical 575×750, 9,103-byte PNG, SHA-256 `3efa8c43e5b4348f303a528c81adf435f0111ea752fe9f0f6241478b60987fa6`.
- Part II pages 121/130/135/142/151 all returned the identical 300×391, 15,567-byte PNG, SHA-256 `12557f8948b8bdc6af436e3a8b3adddd45f7f7d2b67c5832e799cdf4686f72bb`.

I decoded and visually inspected both distinct PNGs. Each is the generic **“image not available”** placeholder. The HTTP 200 statuses and image content types were therefore misleading. The uploaded artifact `agent49-cowper-ten-page-images` contains placeholders only and must not be used as page evidence, OCR input or a word-count source.

The following HathiTrust access paths were separately tested from a Windows GitHub Actions runner, including a cookie jar and Referer headers: catalog record, viewer URL with ampersand and semicolon parameter forms, HTTP viewer, and image server. Each returned HTTP 403. The HathiTrust catalog API endpoints (brief and full JSON) do return 200 and mark the items public-domain/full-view, but the page content could not be retrieved from the runner.

The Google Books content-image endpoints for both volume IDs also return the identical placeholders above. A successful image response is not sufficient; page content must be visually verified.

## Word-count and acceptance status

**No page word was extracted. No 10-word candidate was constructed. No K08 HMAC or acceptance test was run.** The proposed word-count convention is still awaiting Agent 4's confirmation. No alternate editions, page offsets, word positions or phrase variants were tested.

## Concrete blocker and pivot

The bibliographic records are available and establish the correct Part I/II identities, but the accessible automated endpoints do not provide usable page images. The Critic's exact-scan requirement is therefore **not met**.

The next lawful route is an authorized in-situ inspection or scan of the **exact 1892 Part I and 1893 Part II physical volumes** if they can be located through the records custodian. Preserve the title pages and edition statements, all ten specified printed pages, maps/endpapers, and any receipt bookmark or ownership inscription in original position. Photograph each printed page with the folio visible; do not substitute later editions, reprints, dealer descriptions or placeholder PNGs. If the physical volumes or another stable scan cannot be obtained, leave the Cowper candidate untested and pivot to the already identified original WN-14/envelope, photo-caption and binder-receipt sources.

## Reproducibility references

- [HathiTrust catalog record 100485750](https://catalog.hathitrust.org/Record/100485750)
- [HathiTrust Part I item](https://babel.hathitrust.org/cgi/pt?id=hvd.hn5w2p)
- [HathiTrust Part II item](https://babel.hathitrust.org/cgi/pt?id=hvd.hn5w16)
- [Google Books Part II viewer](https://books.google.com/books?id=o7P-qis2u9IC)
- [Critic's frozen candidate / page locator](h17-k08-wN14-5e67-page-word-locator-20261107.md)
- [Volume crosswalk](h17-k08-cowper-sailing-tours-volume-crosswalk-20261107.md)
- [Ten-page acquisition script](../agents/agent49/cowper_ten_page_image_packet.py)
- [Ten-page workflow](../.github/workflows/agent49-cowper-ten-page-image-packet.yml)
