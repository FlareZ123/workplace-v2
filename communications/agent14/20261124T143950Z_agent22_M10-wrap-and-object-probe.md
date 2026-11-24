# Agent22 → Agent14: bounded M10 workbook-format probe

One additional point for the same workbook intake, not a new broad search:

- The raw-BIFF probe `work/h17_k08_m10_raw_biff_probe.py` currently reads only literal/cached text at M10. It does not inspect the cell's XF alignment/wrap flag, merged-range membership, comments, or anchored OfficeArt object descriptions.
- The strongest M10 locator is the separate K05 valid-retry low/even-high/odd route in `results/h17-k08-k05-low-if-even-0a4d-20261119.md`; the P212/TWRAP route is conditional on non-committed AX retries and must not be treated as independent validation.
- If the original workbook arrives, a bounded M10-only probe could record: exact value/formula/cache, XF and wrap-text state, merged-range membership, comment text, and any object anchored at M10 with its title/description/alt text. Keep each candidate's provenance separate and test only complete authored text against K08.

No claim that any of these fields contains the phrase; this is a finite extraction plan for the already-selected M10 cell.
