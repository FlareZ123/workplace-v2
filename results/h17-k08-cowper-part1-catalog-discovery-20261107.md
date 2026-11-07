# Cowper Part I exact-catalog discovery (7 November 2026)

## Question

Is there an independently indexed, authorized digital copy of the frozen Cowper Part I pages, or a different exact Part I item that can be used to recover the missing North words?

## Public metadata queries

A bounded GitHub Actions workflow queried the Google Books Volumes API, Internet Archive Advanced Search, Open Library Search, and the HathiTrust Catalog API using the exact title, author and OCLC number.

- Workflow output: [part1-scan-discovery.json](assets/cowper/part1-scan-discovery.json)
- Workflow file: `.github/workflows/agent24-cowper-part1-catalogs.yml`
- Script: `agents/agent24/cowper_part1_catalog_discovery.py`

Results:

- Google Books Volumes API requests were rate-limited (HTTP 429); they produced no usable alternate volume ID.
- Internet Archive exact-title/creator searches returned no matching item.
- Open Library exact-title/author search returned no matching edition.
- HathiTrust Catalog API returned the authoritative record `100485750`, OCLC `7504145`, for *Sailing tours; the yachtsman's guide to the cruising waters of the English coast*.

The official HathiTrust catalog page identifies Frank Cowper as author, gives the publication range London, L.U. Gill, 1892–1896, and describes five parts. Its viewability list includes **Full view pt.1** at Harvard and **Full view v.2** at Harvard. The Catalog API identifies the Part I item as `hvd.hn5w2p`, enumeration `pt.1`, rights code `pd`, and `Full view`. The HathiTrust full-record API embeds the MARC XML: field 008 encodes the set's 1892–1896 range, field 260 gives London, L.U. Gill, 1892–1896, and field 505 identifies Part I as *The coasts of Essex and Suffolk*. These are set-level bibliographic facts; the item-level title-page imprint remains unverified. The 974 item field's `y=1896` should not be treated as proof that Part I itself was issued in 1896.

- [Official HathiTrust catalog record](https://catalog.hathitrust.org/Record/100485750)
- [HathiTrust Full view Part I item](https://babel.hathitrust.org/cgi/pt?id=hvd.hn5w2p)

The official record establishes that a public-domain Part I full-view item exists. It does not, by itself, verify the exact title-page imprint of the scanned copy.

A title-only Internet Archive search found `sailingtoursyach0000cowp`, a 1985 facsimile of the 1895 edition, 406 pages. Its public metadata marks the item print-disabled/access-restricted and its OCR, page images and text PDF private. It is not the exact 1892 Part I source and is not used as a substitute. See [the IA facsimile comparator report](h17-k08-cowper-internet-archive-1895-facsimile-20261107.md).

## Access boundary and current blocker

The direct HathiTrust viewer link was not accessible through the available web tool (cache miss); earlier automated viewer/image/METS attempts returned 403. The Google Books alias probes for `hvd.hn5w2p` at zoom 1 and zoom 2 returned repeated placeholder images, not page scans. The zoom-1 five-page probe is documented separately in [the placeholder report](h17-k08-cowper-part1-zoom1-placeholder-20261107.md).

No North page word has been extracted. The remaining blocker is obtaining the already-catalogued Part I full-view pages through an authorized human browser/download or an actual physical copy, then checking the printed title-page imprint and page labels.

## Next discriminating action

Have the records custodian open the official HathiTrust Full view pt.1 link above and export the exact pages, including the title page and the five frozen North page labels. If that human route is unavailable, request the David-owned physical copy or a library scan. Do not substitute another edition or launch further arbitrary URL/zoom variants.
