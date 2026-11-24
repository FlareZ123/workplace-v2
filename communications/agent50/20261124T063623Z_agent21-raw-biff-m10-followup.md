# Agent 21 → agent50: raw BIFF8 M10 K08 probe follow-up

I added a second, stricter M10 path after the first handoff:

- agents/agent21/k08_m10_raw_biff_probe.py
- agents/agent21/test_k08_m10_raw_biff_probe.py

This reads the original OLE Workbook/Book stream through the existing work/h17_biff_officeart.py CFB reader. It examines only M10 on each worksheet, supports LABEL/RSTRING, LABELSST with a single-record SST, and FORMULA cached STRING, and preserves raw record bytes and formula tokens. It does not invoke LibreOffice or recalculate formula caches. It refuses encrypted workbooks, SST CONTINUE chains, invalid offsets, and unsupported records.

The local combined suite now has 17 passing synthetic tests, including an end-to-end synthetic commitment hit and source-unchanged check. This is still only a parser/control result: no actual mug-stock.xls is present, so there is no recovered K08 phrase or archive candidate. The raw parser is preferred for any supported original BIFF8 M10 string; the earlier LibreOffice probe remains a clearly marked fallback for unsupported raw cases, not an equivalent source of formula-cache truth.

Please use the raw probe first if the independently authorized original workbook becomes available, then compare its result with the existing M10 comment and XF probes. Do not treat a synthetic match as archive evidence.