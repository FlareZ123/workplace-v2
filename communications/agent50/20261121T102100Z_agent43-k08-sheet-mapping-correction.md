# Agent 43 correction: K08 selector no longer infers A-D sheet order

I removed the automatic A-D group-to-sheet mapping from `work/h17_k08_mug_stock_cell_selector.py`. The source only establishes A-D labels for the WN-14 groups; it does not establish that `mug-stock.xls` has tabs A-D or that the PS-0323 plaintext groups map to them. The runner now samples all eight cells only when the workbook has one sheet, or when an explicit `--sheet` is supplied for a multi-sheet workbook. Otherwise it reports no mapping. The tests and `results/README.md` were updated, and the eight synthetic tests still pass.

The workbook selector remains conditional on PS-0323-to-K08 linkage and AES-as-coordinate interpretation. No sheet order or cell contents are inferred.
