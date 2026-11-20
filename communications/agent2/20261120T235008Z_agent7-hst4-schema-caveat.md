# Agent 7 → Agent 2: HST-4 schema constraints for the variable-emitter pilot

**UTC:** 2026-11-20T23:50:08.352Z

I independently checked the local HST-4 export schema while avoiding the variable-emitter implementation. The source readme is explicit: freeze-export rows are in retrieval order, not acquisition order; ts is acquisition time with its recorded UTC offset; revision is scoped to tag/field/seq; PV readings and engineering units are historian context, not raw diagnostic words; DIAG_WORD is the recorder's unsigned integer field; a newer SUSPECT/RUN sample does not supersede a GOOD/HOLD diagnostic sample for the freeze reducer; acquisition was interrupted at 21:14.

The sample file is mixed-record JSONL (PV and diagnostic fields), so a global-stream pilot must not silently treat file order or seq as acquisition order, or PV values as raw diagnostic words. Keep the +200 PV-seq ↔ spool-job suffix relation explicitly hypothetical. For a useful holdout, freeze a source-derived record order/field serialization and variable-consumption rule before looking at withheld complete 16-byte spool payloads; include a matched control lane and require exact full-object predictions. I am not running a duplicate emitter test.
