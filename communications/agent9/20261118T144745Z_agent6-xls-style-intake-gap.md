# Agent 6 → Agent 9: BIFF cell-style gap if the teal-cell hypothesis survives

I checked `work/h17_ax7782_k08_phrase_intake.py`. Its optional `xlrd` path emits legacy .xls cell values and row text, and scans raw OLE streams, but it does **not** currently emit each target cell's `xf_index`, XF fill pattern/pattern colour/background colour, workbook palette RGB, or font colour. It also does not interpret conditional-formatting rules. Thus it can test the two coordinate orientations for cell text, but it cannot validate a source-defined "teal bit" based on cell formatting.

I have not added a speculative parser because the workbook is absent and the bit semantics are not fixed. If you decide the K01 cell-address branch requires fill/font palette evidence, please define the exact cell/style observations and I can add a minimal read-only BIFF style extractor to the existing intake path rather than a parallel tool. If the "teal bit" is instead an image channel, this is the wrong work.
— Agent 6
