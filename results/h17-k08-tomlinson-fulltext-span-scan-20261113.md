# K08: full-text exact-span exclusion for Tomlinson's *The Sea and the Jungle*

**Date:** 2026-11-13  
**Agent:** 40  
**Status:** bounded negative; no K08 candidate recovered

## Question

Does H. M. Tomlinson's *The Sea and the Jungle* contain the exact normalized K08 phrase as a contiguous span? This extends the earlier 913-token saloon-passage check to the full book, motivated by the map-back-book / sea / night-watch / table-voices clues.

## Source and method

- Full text: [GITenberg mirror of Project Gutenberg eBook 37205](https://github.com/GITenberg/The-Sea-and-the-Jungle_37205/blob/master/37205.txt), the 1920 text edition (597,696 bytes).
- Normalization: lowercase; replace every character outside ASCII `a-z0-9` and whitespace with a space; collapse whitespace; trim.
- Candidate: each contiguous normalized token span, lengths 1 through 16 words.
- K08 construction: `HMAC-SHA256(key=desk_nonce, message=normalized_phrase)[:16]`.
- Acceptance check: `SHA256(component)` against the unchanged K08 slot commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.
- The optimized HMAC/SHA-256 implementation was checked against the local Python standard-library calculation for a known sample phrase before the sweep.

## Results

- Normalized source tokens: **108,170**.
- Contiguous spans checked:
  - lengths 1–4: included in the 1–4/6–10 batch;
  - length 5: **108,166**;
  - lengths 6–10: included in the 1–4/6–10 batch;
  - lengths 1–4 and 6–10 combined: **973,489**;
  - lengths 11–16: **648,945**.
- Total exact candidates checked: **1,730,600**.
- Original K08 commitment hits: **0**.

A separate source-wide scan of all 43 textual files in the supplied export checked **634,096** contiguous normalized spans of 1–40 words, also with **0** K08 hits.

The five-page/word-103 coordinates (81, 94, 99, 106, 112) applied to the 1920 Tomlinson page markers yield `of / nerves / world / after / distance`, not a phrase. This is only a Tomlinson-edition check; it does **not** test the distinct 1947 Praeger five-page hypothesis.

## Interpretation and limits

The full-text result closes the direct-contiguous-quotation hypothesis for the Project Gutenberg text of *The Sea and the Jungle*; it is materially stronger than the earlier excerpt-only scan. A reprint with the same text cannot restore a contiguous-span hit merely by changing pagination.

It does **not** exclude:
- a non-contiguous book cipher or a phrase assembled from multiple passages;
- a paraphrase or author-final caption inspired by the book;
- a different book or a different source carrier;
- the separate Praeger 1947 edition/page-word hypothesis.

Do not repeat a generic contiguous-span sweep of this text. Any return to this book should introduce a source-motivated non-contiguous construction with a frozen finite rule. Otherwise prioritize the author-final document/version path or a distinct complete K04 constructor.
