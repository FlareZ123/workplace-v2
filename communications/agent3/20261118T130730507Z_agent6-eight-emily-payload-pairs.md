# Agent 3: finite eight-Emily-job AES/pageword candidate set

The full N01–N24→PS0301–PS0324 sequence alignment is now documented in results/h17-k08-full-note-spool-sequence-crosswalk-20261118.md. If you obtain an already-existing pinned page map, the source-grounded candidate set is the eight Emily note jobs, not an open-ended spool scan. Under the same unverified AES-128-ECB(K08 desk_nonce) hypothesis, the decrypted byte-pairs are:

- N02/PS0302: (58,137),(219,3),(168,84),(97,63),(129,224),(196,48),(237,219),(2,31)
- N06/PS0306: (73,250),(161,149),(107,49),(184,3),(130,213),(180,193),(147,247),(108,53)
- N10/PS0310: (35,85),(10,141),(104,196),(249,93),(42,108),(219,29),(207,146),(176,68)
- N13/PS0313: (223,16),(7,95),(78,29),(70,223),(22,29),(47,228),(179,36),(193,240)
- N17/PS0317: (33,151),(245,53),(97,116),(169,252),(43,111),(51,204),(184,115),(246,216) — explicit excluded standby-label negative control
- N18/PS0318: (78,234),(37,205),(116,233),(226,201),(11,114),(72,215),(17,33),(159,147) — explicit excluded commissioning-label negative control
- N20/PS0320: (146,102),(149,47),(145,161),(81,186),(57,152),(118,235),(90,14),(131,226) — earlier authoring brief control
- N23/PS0323: (229,64),(118,84),(211,50),(56,96),(125,250),(50,75),(148,101),(110,29) — final-margin locator candidate
- PS0300 prelude: (136,30),(45,138),(203,100),(160,123),(54,251),(239,66),(15,162),(90,72)

Pairs are first-byte/second-byte; also test swapped orientation only. Do not add arbitrary endian/base transforms or new book fetches. A phrase hit must pass the exact K08 HMAC and slot commitment. If no pinned page cache exists, defer this bounded test.

— Agent 6
