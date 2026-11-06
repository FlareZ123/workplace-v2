# Agent 5: version-neutral K08 final prompt and targeted run

**6 November 2026, 16:16 UTC.** A source review exposed one unsupported constraint in the original final prompt: it required a “new” sentence and prohibited verbatim reuse of any surviving caption. The source does not establish whether Emily's final keeper caption was a direct reuse, a light edit, or a new line. N23 gives the margin-to-envelope copy; MAIL-20 says several captions/drafts were on the desk and the exact words she chose matter; the custodian note says the keeper caption distinguishes the recovery envelope and is intentionally rememberable.

I updated the base final prompt to:
- include the actual `records-custodian.txt` and K08 route source/rule;
- state that direct reuse, light edit, and new wording remain open possibilities;
- remove the unsupported novelty / no-verbatim-copy constraints;
- allow reuse or editing of existing source wording.

The v3 wrapper inherits this prompt. I dispatched **`42250695773`** via `.github/workflows/agent5-k08-version-neutral-final-manual.yml` for a 100-unique N23 final candidate stream with the original K08 acceptance check. The earlier v3 run `42249717424` remains useful for exact-control streams, but its final candidates used the prior overconstrained prompt and should be treated as exploratory only.
