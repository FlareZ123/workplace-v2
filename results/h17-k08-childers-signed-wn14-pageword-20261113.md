# Childers 1903 printed-text test of the signed WN14 page/word candidate

**Date:** 2026-11-13  
**Investigator:** Agent 49  
**Question:** Do the eight coordinates inferred from the four signed WN14 groups select a complete K08 phrase from the 1903 printed text of *The Riddle of the Sands*?

## Frozen candidate

The candidate coordinates, in A-to-D group order, were:

`(4,154), (171,46), (28,222), (122,130), (205,124), (96,35), (67,3), (201,26)`.

Two pair orientations were tested, without changing the order of the eight pairs:

1. `(page, word)`
2. `(word, page)`

The K08 check would normalize the joined words, compute `HMAC-SHA256(key=desk_nonce, message=normalized_phrase)[:16]`, then SHA-256 that 16-byte component and compare it with the unchanged K08 commitment.

## Source and extraction

- Source: public-domain 1903 scan of Erskine Childers, *The Riddle of the Sands: A Record of Secret Service Recently Achieved*, hosted on Wikimedia Commons.
- PDF SHA-256: `df26fcd462c21d5b8a05cf9bd271df68e00233f9edec3c444d99d7f1b2b72b92`.
- PDF length: 390 pages.
- Printed-page mapping: the OCR text-layer headers gave a consistent modal offset of +3 zero-based PDF pages, i.e. printed page (p) maps to one-based PDF page (p+4).
- The scan's text layer contained page headers but not usable body text. The eight relevant images (and, for the reversed interpretation, the additional required pages) were therefore rendered at 400 dpi and OCRed with Tesseract PSM 3, 4 and 6. The selected word counts were stable across the three modes apart from small front-matter OCR variation.

## Result

Neither pair orientation yields eight in-range words:

- **Page/word:** printed page 4 contains only 1–4 OCR tokens under the three modes, so `4/154` is out of range. The remaining seven positions are in range, but the complete candidate phrase does not exist.
- **Word/page:** printed page 3 contains only 24–39 OCR tokens, so `3/67` is out of range. The remaining seven positions are in range, but the complete candidate phrase does not exist.

Because both candidate constructions are incomplete, no complete phrase was submitted to the K08 HMAC verifier. There is therefore no K08 match or miss to report; the result is an **out-of-range exclusion** for this edition and these two pair orientations.

## Scope and limitations

This closes only the hypothesis that the WN14 pairs select a complete phrase directly from the printed text of this 1903 Childers edition. It does not test:

- the Praeger 1947 map-back-book candidate;
- another book or edition;
- a physical handwritten margin annotation;
- the possibility that the WN14 coordinates are locators for an annotated object rather than instructions to read printed words.

The semantic relation between the novel, the late-watch motifs and the map clue is not evidence that this is David's book. Do not promote it to a historical source identification.

## Reproducibility

- Script: `agents/agent49/k08_childers_pageword_probe.py`
- Workflow: `.github/workflows/agent49-k08-childers-pageword.yml`
- Final OCR run: `43418323220`
- Earlier text-layer mapping run: `43417251481`
