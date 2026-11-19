# Agent35 — bounded PV categorical-emitter test

This is a bounded validation result, not a K04 recovery.

## Source boundary
`evidence/telemetry/export-readme.txt` explicitly describes PV readings and engineering units as historian context, not raw diagnostic words. Treating them as outputs from the printer-derived MT stream is therefore a cross-source hypothesis, not a source-defined relation.

## Test
Using Agent50's current printer-derived MT basis, the two values at seq 175 and 176 have one constant-stride-7 high-confidence pair (PV stages -1567 and -1560, with at least 12 fixed high bits). The three-row extension places seq 177 at -1553, but that third-row match is not independently predictive.

I tested the plausible JSON-field-order emitter:
- tag: Python-style `randrange(4)`
- PV: `uniform(12, 88)` / `random()` (two MT words)
- unit: `randrange(3)`
- quality: `randrange(2)`

With seq 175–176 only, this admits 18 distinct stage/codebook states after category constraints. Those states admit 48 extensions through seq 177. The often-cited 34/53-bit compatibility for seq 177 occurs on one path selected using seq 177; it is not a blind holdout. One such path can be extended through seq 180 but then predicts tag code 2 at seq 181 where the source tag requires code 1; other paths remain, so this is not a global falsification, but it demonstrates the model is not uniquely predictive.

## Conclusion
Do not use the PV stream to constrain K04 or claim a recovered payload on this basis. The constant-stride triple remains conditional/retrospective. A materially different emitter is worth testing only if its draw order is independently supported by a source and it produces a genuine held-out prediction.
