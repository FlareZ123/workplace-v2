# Cowper Part I zoom-1 page-image probe: placeholder confirmed (7 November 2026)

## Question

Does the frozen Part I Google Books image route return actual page images for the five North page labels when requested at `zoom=1`, the parameter difference identified by the Critic after the Part II page-130 thumbnail was found?

## Method

A manual GitHub Actions workflow requested only the exact HathiTrust Part I item alias `hvd.hn5w2p` and the frozen page labels in binder-tab order:

`PA94, PA81, PA106, PA99, PA112`

Each request used the Google Books image endpoint with `img=1`, `zoom=1`, and `hl=en`. The workflow saved the PNG responses and recorded HTTP status, content type, dimensions, byte count, final URL and SHA-256.

- Workflow: [42360860566](https://github.com/FlareZ123/workplace-v2/actions/runs/42360860566)
- Manifest: [Part I zoom-1 manifest](assets/cowper/part1-1892-zoom1/manifest.json)

## Result

All five requests returned HTTP 200 and `image/png`, but every page label returned the same image:

| Printed page | Bytes | Dimensions | SHA-256 |
| ---: | ---: | ---: | --- |
| 94 | 1,269 | 128×170 | `e3f8c414b288cbdf4e6d1e00eb6d3826157d10a5b5628b9318f726ea490eca12` |
| 81 | 1,269 | 128×170 | same |
| 106 | 1,269 | 128×170 | same |
| 99 | 1,269 | 128×170 | same |
| 112 | 1,269 | 128×170 | same |

The five identical hashes across distinct page labels establish that these are a repeated placeholder response, not five Cowper pages. HTTP 200 and PNG content type are insufficient evidence of page access.

## Interpretation and stop rule

This closes the bounded Part I `zoom=1` route. The earlier `zoom=2` alias probe returned the generic “image not available” placeholder (SHA-256 `3efa8c43e5b4348f303a528c81adf435f0111ea752fe9f0f6241478b60987fa6`). The ordinary Google Books viewer for `hvd.hn5w2p` returned 404; HathiTrust viewer/image/METS routes returned 403 in the existing probes. Do not launch arbitrary zoom, language, host or page-label variants without a new source-backed reason.

The official HathiTrust catalog record [100485750](https://catalog.hathitrust.org/Record/100485750) identifies the work as published London, L.U. Gill, 1892–1896, in five parts, and lists **Full view pt.1** at Harvard. The Catalog API identifies that Part I item as `hvd.hn5w2p`, enumeration `pt.1`, public-domain rights, and Full view. A separate item-level 974 field previously surfaced 1896, so the exact title-page imprint of the scanned copy still needs visual confirmation. The direct [HathiTrust Full view pt.1 link](https://babel.hathitrust.org/cgi/pt?id=hvd.hn5w2p) is official, but it was not accessible through the available web tool (cache miss) and earlier automated viewer/image/METS requests returned 403. The catalog discovery and API results are documented in [Part I catalog discovery](h17-k08-cowper-part1-catalog-discovery-20261107.md). No North word has been read or extracted.

## Next source required

Obtain an authorized scan of the exact 1892 Part I copy or inspect the David-owned physical volume. Preserve the title-page imprint, printed page labels and original map verso. Until then, the frozen ten-page Cowper candidate cannot be assembled or tested against K08.
