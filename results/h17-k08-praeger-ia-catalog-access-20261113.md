# Praeger *The Way That I Went*: public scan-access result

**Date:** 2026-11-13  
**Investigator:** Agent 49  
**Question:** Can an unrestricted digital copy of the map-back-book candidate be obtained to test the WN14 page/word and physical-margin hypotheses?

## Method

A read-only Internet Archive metadata search was run for the exact title with author and text-media filters, then for the title alone. Public metadata was retrieved for each returned item. The probe did not download OCR, page images, PDFs, EPUBs, or other book content; it did not borrow or attempt to bypass any access restriction.

## Findings

The Internet Archive catalogue returned three records for *The Way That I Went*:

| Identifier | Catalogue year | Collection/access classification |
|---|---:|---|
| `bwb_KU-429-532` | 1947 | `internetarchivebooks`, `printdisabled`, `inlibrary` |
| `bwb_KU-389-133` | 1939 | `internetarchivebooks`, `printdisabled`, `inlibrary` |
| `bwb_KV-165-111` | 1947 | `internetarchivebooks`, `printdisabled`, `inlibrary` |

The metadata inventories OCR, scan-data, PDF and LCP-EPUB file entries for these records. Their collection classifications indicate controlled/in-library access; this investigation did not attempt to retrieve those contents. The public Google Books API probe for volume `uT5RAQAAIAAJ` returned HTTP 429, so it did not establish viewer access.

## Interpretation

- The suspected 1947 edition is represented by two Internet Archive catalogue records; a 1939 record also exists.
- This confirms that digitized scans exist as catalogue objects, but does **not** establish unrestricted page-text access or identify David's physical copy.
- The local evidence's North/South ticket-page crosswalk remains a reason to retain the 1947 Praeger edition as a candidate. The map and tea-receipt clues, together with N23's reference to a margin, may point to a *particular annotated physical copy*, not to the printed text of an arbitrary scan.
- No phrase, page-word extraction, handwriting, or K08 component was recovered here.

## Next useful source

Obtain an authorized scan or photographs of the relevant pages **including their margins**, ideally from David's actual map-back copy, with the title page, edition statement and tea-receipt bookmark visible. The WN14-derived page/word candidate is `4/154, 171/46, 28/222, 122/130, 205/124, 96/35, 67/3, 201/26`; these are candidate locators, not verified coordinates for this title. Do not treat the catalogue records as the annotated copy or bypass their access classifications.

## Reproducibility

- Script: `agents/agent49/praeger_public_catalog_probe.py`
- Workflow: `.github/workflows/agent49-praeger-public-catalog.yml`
- Successful metadata workflow runs: `43416526817` and `43416570493`
- No book-content files were downloaded.
