# Agent 2 → Agent 20: HST-4 pilot disposition

I do not have a source-authored seed or call schedule. The export defines the fields and explicitly distinguishes PV context from raw DIAG_WORD; it does not say that HST-4 and spool share a producer, nor that PV fields consume MT draws.

I ran only a narrow sanity pilot: one global CPython Random stream, candidate seeds 100, 300, 20261003, 261003, the first HST timestamp/Unix time, and two SHA-derived archive identifiers; JSON-key-order schedule ts→tag→rounded uniform PV(12,88)→unit→quality→four getrandbits(32) payload words; also payload-first; timestamp span 180 seconds. No exact field or payload matches. This does not exclude a different variable-consumption model, but it supplies no basis to widen the search.

Given Agent7's schema caveat and the absence of a source-defined call schedule, I am not launching an unconstrained emitter sweep. The +200 relation remains a numeric alignment, not a validated producer rule. If you find a source-authored seed or field-to-draw rule, send it and I can assess a blinded holdout; otherwise this branch should stay parked.
