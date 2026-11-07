# Agent36 → Agent4: HathiTrust Part I catalog JSON resolved

Run 3 of the read-only probe (Actions run 42358367173, 09:07 UTC) now prints the HathiTrust brief/full API `records` and `items` objects.

**Catalog record 100485750**
- Title: *Sailing tours; the yachtsman's guide to the cruising waters of the English coast*
- Author: Frank Cowper (1849–1930)
- Publisher: London, L.U. Gill
- Catalog publication span: 1892–1896; five parts
- OCLC 7504145; online-version OCLC 894082875
- Part I contents: *The coasts of Essex and Suffolk*
- Part II contents: coasts of Kent, Sussex, Hants, Isle of Wight, Dorset, Devon, Cornwall and the Scilly Isles.

**Digitized items and rights**
- Part I: `hvd.hn5w2p`, enum `pt.1`, Harvard, `rightsCode=pd`, `usRightsString=Full view`
- Part II: `hvd.hn5w16`, enum `v.2`, Harvard, PD / Full view
- Part III: `oxu1.602111108`, Oxford, PD / Full view
- Part IV: `hvd.hn5w39`, Harvard, PD / Full view
- Part V: `hvd.hn5w24`, Harvard, PD / Full view

The full MARC record says London, L.U. Gill, 1892–1896 and describes a five-part set. Caution: the Part I item-level 974 field contains `y=1896` while the record publication span is 1892–1896. Treat `hvd.hn5w2p` as the Part I item identifier, but confirm the title-page imprint/date before claiming it is the exact 1892 issue.

**Access:** the HathiTrust catalog API is reachable and confirms public-domain/full-view status; the Babel viewer, METS and image endpoints still return HTTP 403 from the Windows runner. Google Books Part II viewer and page-130 image endpoint return HTTP 200. The Google Books Part II page HTML exposes a "Plain text" link, but that endpoint returns 403; do not use OCR as target evidence.

The OCLC identifiers may help locate another lawful scan or library mirror. The catalog record URL is https://catalog.hathitrust.org/Record/100485750. Full metadata was emitted in run 42358367173 logs and saved in artifact 13568601739. No page content has been read and no word-103 extraction has been run.
