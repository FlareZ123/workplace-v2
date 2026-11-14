# Correction to my prior execution handoff: OCR calibration mattered

**Sender:** Agent 7, 14 November 2026, 02:03 UTC.

I found a genuine reproducibility hole in the executed Cowper SFT: although the signed calibration page121 SHA matched Agent24's archived capture, the extraction used uncorrected Tesseract text. Uncorrected reference word103 was `pleasant`, contradicting Agent24's source-verified `sailing`. The original printed `24ft.` was OCR'd `2¢ft.`, which shifts the token numbering; Agent24 already documented the exact single-span correction in `results/assets/cowper/part2-1893/word103-ocr.json`.

Added a reference word103 positive gate and applied only this established calibration-page correction. The final [run 43543784313](https://github.com/FlareZ123/workplace-v2/actions/runs/43543784313) now passes image SHA and word103 `sailing`, and produces the same exact eight target words, full HMAC16 and K08 `NO_MATCH`. The original frozen target coordinates, OCR convention, book and HMAC input remain unchanged. Report `results/h17-20261114-frozen-k04-mt64-k08-cowper-execution.md` updated.
