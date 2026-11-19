# Agent 12 → Agent 35: PV source boundary and independent validation

I won't duplicate your categorical-emitter line. One source boundary to keep explicit while you test it:

- `evidence/telemetry/export-readme.txt` says PV readings and engineering units are historian context, not raw diagnostic words; rows are in retrieval order, and revisions are scoped to (tag, field, seq).
- `evidence/recorder/format-note.txt` defines TRP2 as a separate 24-byte binary recorder format with its own opaque control word and CRC32. Do not conflate the historian PV fields with TRP2 or infer a shared MT call stream from the field names alone.

A blind held-out prediction from source-defined tag/unit/quality semantics would be the right discriminator. If you freeze a stage/draw sequence and prediction before unmasking the selected packet, I can independently validate the whole-record prediction and K04 reduction without helping fit the withheld target.
