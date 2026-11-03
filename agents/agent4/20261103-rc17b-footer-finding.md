# 3 Nov 2026: new RC-17 B footer cross-carrier discovery

Under speculative p951 MT19937, the original revision B footer VERIFY C130C9BB matches native -186 at 32/32 fixed bits and PURGE 759E0027 matches adjacent -185 at 26/26. Same tempered, little-endian view. A source-only scan of all 12 RC-17 B/C/D footers found exactly those two matches (minimum 14 fixed bits). The recovered pair is a new source-model connection, not proof of original generator firmware.

Tentative reverse B fourword positions -186..-183 add 65 independent equations (printer-only basis rank 15365 to 15430); positions -184/-183 have no independent fixed bit witnesses. K04 selected quotient remains 128/128 unknown. Separate original-target candidate tests of 2304 revision footer layouts and 23040 cross-doc/spool XOR layouts found no matches. K08 final words not recovered.

Published analysis: results/h17-k04-rc17-b-consecutive-mt-footer-bridge.md; runnable SFTs: agents/agent4/k04_rc17_b_document_donor_sft.py and agents/agent4/k04_rc17_footer_relocation_sft.py. Broadcast 20261103T0910Z_agent4-rc17b-consecutive-mt-anchor.md.

Next: identify original independent document generation order/copy bridge, use a withheld page source-value prediction to validate the tentative remaining B positions, and seek target-reaching future donors (1179..1181, 1347/1348, 1574/1575) rather than arbitrary seed attrition. Original six PASS, K04/K08 unresolved, combined INCOMPLETE.
