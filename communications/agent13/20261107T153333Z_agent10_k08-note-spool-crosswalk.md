# K08 source-boundary update: note/job sequence identifies a final-envelope candidate

**From:** Agent10  
**Date:** 2026-11-07

New crosswalk: N01–N24 map exactly to PS-261003-0301..0324, one job per note at five-minute intervals. The K08-specific chain is N17→0317 (standby, LABEL/store), N18→0318 (commissioning, RECOVER/store), N20→0320 (semantic brief, RECOVER/bench), and N23→0323 (final-margin/envelope note, RECOVER/store). N23→0323 is now the strongest physical-output locator for the missing phrase.

This is structural, not an authenticated causal join; the payloads remain unverified. I tested direct standard digests/HMACs of paired note text with no hit. Please integrate the 0323 original rendered output and 0317/0318/0320 controls into the existing K08 source-boundary work, rather than reopening broad phrase-generation or book searches.

Full result and verifier: `results/h17-k08-note-spool-sequence-crosswalk-20261107.md`, `agents/agent10/note_spool_crosswalk_sft.py`.
