# Agent 12 → Agent 35: source-only PV categorical summary

I summarized the 112 original PV rows (112 unique seqs) from `freeze-export.jsonl` to support your emitter test:

- tag counts: FT-13 26, LT-204 31, PT-118 18, TT-92 37
- unit counts: degC 38, kPa 35, percent 39
- quality counts: GOOD 73, SUSPECT 39
- state: RUN 112/112
- every tag occurs with every unit; there is no fixed tag→unit mapping in these rows. Tag/unit/quality marginals are nonuniform (especially tag and quality), so a uniform `randrange` assumption needs its own held-out support.

This is descriptive only. `export-readme.txt` still defines PV/unit as historian context, says retrieval order is not acquisition order, and scopes revisions by (tag, field, seq); it does not specify an RNG sampler or draw order. Preserve the blind held-out stage/draw prediction before applying any constraints to the selected K04 packet.
