# K04: decrypted BX25/08 PDF streams provide 5,410 newly visible 16-byte source carriers

**Agent 43 | 6 November 2026 | genuine original K04 NO_MATCH.** Six accepted REC8/1 components unchanged; K04 and K08 remain missing; combined recovery INCOMPLETE.

## New source representation

The attached October preservation ZIP contains encrypted 2025 property PDF `evidence/h17-supplemental-office-files/BX25-08.pdf`. Its original SHA256 is `b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425`. Original retired-office bookmarks establish a four-digit old scanner release setting; the unique password `8131` was independently recovered in workplace-v1 on 20 October and is prior art, **not** an archive-recovery secret. The original PDF page identifies `FA-17` north office printer/cassette and the separate `FA-18` archive station. It was created in 2025 and does not attest the October 2026 coupon.

Prior original carrier audits swept raw bytes and hex spans of all **46 ZIP member bodies**. Those scans read the PDF's **encrypted streams**. Here the source-derived representation is the decrypted PDF document, its actual page text and all decoded original PDF object streams. This is a new container decoding class, not a duplicate raw-member search.

## Exact original-data construction

Source ZIP SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`. Read-only PyMuPDF 1.26.7 authenticated the original single PDF page with the previously documented `8131` setting, then emitted the decrypted non-deflated PDF representation, extracted original page text, and extracted 10 decoded xref object streams, making **12** source-derived binary views.

For every derived view, take every raw 16-byte window and every 16-byte decoding of a 32-hex-digit window in a maximal hexadecimal run, including all shifts. Deduplicate source carrier bytes before checking K04. Independently generate the same source-carrier class from the 46 original ZIP member bodies to measure **actual overlap**.

| Source-carrier set | Distinct 16-byte values |
| --- | ---: |
| Previously swept raw 46-member original content | 67,470 |
| Decrypted PDF, decoded object streams, rendered page text | 6,585 |
| Decrypted-source carriers already in original-body set | 1,175 |
| **New original-derived 16-byte candidates** | **5,410** |

For every one of the 6,585 complete decoded candidates `X`, perform three different K04 reductions against the unchanged original full 256-bit SHA256 commitment:

1. Physical coupon `X` XOR authentic route mask `8556C8CB6140A7F9A5123AC7571BEE1C`.
2. Original copied ACK2 `A9A9DC5731A5E2AE879C47215C2559D5` XOR alternative mask `X`.
3. Already-reduced component `X` itself.

Every role uses immutable original SHA256 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. The search performs **19,755 full original K04 comparisons** across the three roles, of which **16,230** use newly exposed 5,410 candidate carriers. **Zero commitment hits in all three roles.**

Synthetic positive control: construct a separate whole SHA256 digest from the lexicographically first novel decoded carrier XOR the original mask, and confirm the same enumerator locates that carrier **exactly once**; this passed. The original zip/PDF source SHA pins, 46 source files, 12 derived views and all set sizes passed. Executed locally against the original unmodified user ZIP; no remote CI execution claimed. [Standalone read-only reproducer](../agents/agent43/k04_bx25_decrypted_pdf_carrier_sft.py) requires PyMuPDF and takes the original ZIP path or repository resources directory.

## Evidentiary limit and next move

This excludes the exact direct decoded-PDF raw/hex carrier and alternative-mask models. A 2025 property declaration is a weak candidate for containing a 2026 physical printer output, and its absence of a target hit is unsurprising. The result matters as a **completed genuinely different decoded original-source carrier class** and should prevent repeating old encrypted-blob rescans. It does not identify the physical original coupon or an issuer algorithm, and no K04 physical bit has been authenticated. K08's final desk-margin wording is also unquoted. A contemporaneous exact selected ACK media witness or a genuinely predictive producer/copy rule remains necessary.
