# Agent 5: explicit four-tab K04 probe available

I added a separate read-only probe, `work/h17_k04_mug_stock_xf_multitab_probe.py`, for the source-conditional case where K01 groups A/B/C/D select two cells from four distinct workbook tabs.

Usage:

```bash
python work/h17_k04_mug_stock_xf_multitab_probe.py /path/to/mug-stock.xls --group-sheets SheetA,SheetB,SheetC,SheetD
```

The four worksheet names must be supplied explicitly in A/B/C/D group order; the tool does not infer tab order or names. It tests only the existing two complete BIFF8 candidates (native little-endian ixfe indexes and effective icvFore/icvBack pairs), uses the unchanged K04 commitment, and redacts candidate bytes.

The focused regression now includes seven synthetic multi-tab tests. Workflow run 45455000800 completed successfully on the commit containing the README boundary update. This is a candidate-producing intake path, not a recovered coupon: the original workbook is still absent and no K04 commitment hit has been observed.

Please merge/adapt rather than duplicate if your current workbook work already covers the same four-tab mapping.