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

The HathiTrust catalog identifies the item as Part I / PD / Full view, but its item-level 974 date is 1896. The exact printed title-page imprint therefore remains unverified against the required 1892 issue. No North word has been read or extracted.

## Next source required

Obtain an authorized scan of the exact 1892 Part I copy or inspect the David-owned physical volume. Preserve the title-page imprint, printed page labels and original map verso. Until then, the frozen ten-page Cowper candidate cannot be assembled or tested against K08.
