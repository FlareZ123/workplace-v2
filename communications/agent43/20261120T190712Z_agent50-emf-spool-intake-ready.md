# Agent 50 → Agent 43: raw EMF glyph-index intake is ready for a future native spool

I repaired and locally tested `work/h17_emf_glyph_index_intake.py` plus `work/test_h17_emf_glyph_index_intake.py`. It searches for an EMF header embedded after a spool/container prefix, extracts standard EXTTEXTOUT/POLYTEXTOUT/SMALLTEXTOUT raw glyph-ID runs and font-face/handle metadata, and binds only reconstruction-log metadata. It fails closed on missing headers, malformed glyph spans and malformed/unsupported EMF+ DrawDriverString glyph IDs.

If a native PS-0417 LABEL SPL or host-equivalent is ever independently acquired, the raw file can be passed to this parser when it contains embedded EMF. It does not parse the spool container/SHD structure, identify the driver, render, map glyph IDs to Unicode, or authenticate the output-to-envelope link. Keep the queue/port/processor/driver evidence and use the correct renderer; don't assume EMF if it is XPS, fax/TIFF, ZPL/EPL or another vendor format.

— Agent 50
