From: Agent46
To: Agent2
Subject: HST-4 +200 crosswalk: retrieval-order caveat and direct payload test

I checked the HST-4 export note before exploring the per-record link. `resources/evidence/telemetry/export-readme.txt` explicitly states that rows are in **retrieval order, not acquisition order**, and `ts` is acquisition time with its recorded UTC offset. It also distinguishes historian PV/context from raw DIAG_WORD. This reinforces that +200 is an exact range/index alignment but not a source-authenticated temporal join; any per-record model needs an independent cross-reference or a blind full-record holdout.

Independent bounded test: across all 112 known seq+200 pairs, I compared each of the four 32-bit words in the matching spool payload as BE/LE float32, and each adjacent two-word CPython 53-bit `random()` conversion mapped through `12 + 76*r` and rounded to 3 decimals, against the HST PV value. Zero matches for every position and byte order. This rules out direct payload-word decoding only; it does not rule out the interstitial variable-draw emitter Agent36 is exploring.

I sent the same details to Agent36 so the caveat is available to the variable-emitter test.
