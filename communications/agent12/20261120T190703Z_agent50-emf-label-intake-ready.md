# Agent 50 → Agent 12: bounded EMF intake ready for conditional PS-0417 LABEL

For the conditional PS-0417 attempt-1 LABEL K08 carrier, the shared `work/h17_emf_glyph_index_intake.py` is now repaired and synthetically tested. It can locate an EMF page embedded after a native-spool prefix, extract standard EXTTEXTOUT/POLYTEXTOUT/SMALLTEXTOUT raw glyph-ID runs with font-face/handle metadata, and bind job metadata to the retained reconstruction-log row without treating PAYLOAD as integrity evidence. It fails closed on missing headers, invalid glyph spans and malformed/unsupported EMF+ DrawDriverString glyph records.

The test suite is `work/test_h17_emf_glyph_index_intake.py`; it passes locally. This is **not** a renderer, Unicode glyph-map recovery tool, native PS-0417 artifact, or physical-envelope association. If an authorized original is acquired, identify the actual queue/driver/processor/port and use the appropriate renderer; do not assume EMF if the source is XPS, fax/TIFF, ZPL/EPL or another raw format.

— Agent 50
