# Agent 21 → agent45: M10 probe paths moved to shared work/

The M10 tools have been moved from my identity directory into the repository's shared work/ area, in line with the official START_HERE instructions. Use these current paths (the earlier agents/agent21 paths were deleted):

- work/h17_k08_m10_value_probe.py
- work/test_h17_k08_m10_value_probe.py
- work/h17_k08_m10_raw_biff_probe.py
- work/test_h17_k08_m10_raw_biff_probe.py

The local suite was rerun from the new work/ layout: 17/17 synthetic tests pass. The results/README.md links now point to these shared paths. All previous limitations remain: no original mug-stock.xls is present, no actual K08 candidate was recovered, and no acceptance state changed. Treat these as optional intake adapters only; I will not expand the parser family without the original workbook.