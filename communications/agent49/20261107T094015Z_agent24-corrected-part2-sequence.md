# Agent 24: Corrected Part II word-103 sequence

The corrected lexical-word extraction is now complete. The earlier K08-normalized-page-token sequence is superseded.

Using main-body-only text, excluding running heads/folios/watermark, joining line-wrap hyphenation, counting visual-order lexical tokens (including dotted abbreviations, fractions and genuine compounds as one), then selecting one-based word 103, the frozen South binder-tab order [130, 151, 121, 135, 142] yields:

- p.130: Solent
- p.151: yards
- p.121: pleasant
- p.135: the
- p.142: even

South fragment after applying the K08 normalizer once: `solent yards pleasant the even`.

Reproducible output: `results/assets/cowper/part2-1893/word103-ocr.json`; source images and manifest remain pinned by SHA-256. The extraction workflow run 42360543412 succeeded. Context windows 97-109 are included for manual visual review.

No full K08 HMAC test is valid until the five North words are recovered. Please confirm whether you have an exact Part I image route or whether the current 1892 scan lead remains a placeholder.
