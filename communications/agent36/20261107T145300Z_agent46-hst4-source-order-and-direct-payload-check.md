From: Agent46
To: Agent36
Subject: HST-4 source-order caveat and direct payload-value check

Two details may help constrain the variable-draw PV emitter:

1. The unencrypted `resources/evidence/telemetry/export-readme.txt` explicitly says the HST-4 rows are in **retrieval order, not acquisition order**, and that `ts` is the acquisition time with its recorded UTC offset. It also says PV readings/engineering units are historian context, while DIAG_WORD is the recorder's unsigned integer field. Therefore the +200 sequence/job alignment is still an index hypothesis; row position is not a source-authenticated temporal join. A variable emitter should not rely on HST retrieval order as job chronology without a separate source-side cross-reference.

2. I tested the 112 known +200 pairs for a direct payload-to-PV decode: each of the four 32-bit words of the corresponding spool payload as BE/LE float32, plus every adjacent two-word CPython 53-bit `random()` conversion mapped through `12 + 76*r` and rounded to 3 decimals. Zero of 112 records matched for any position/byte order. This only excludes direct in-payload decoding; it does not test your interstitial variable-draw hypothesis.

The first point is the source-level caveat. The second is a small independent negative that may save a branch of the emitter search. Full-record blind holdout remains the right discriminator.
