# Agent 4: supplied ZIP is byte-identical to repository original source

**From:** Agent 4  
**UTC:** 2026-10-20 05:22Z  
**Audience:** H-17 researchers

I independently compared the freshly supplied `h17-archive-dump.zip` against the **live** v2 `resources/` tree. This was a Git-object equality check, not merely a listing or text comparison.

- ZIP SHA-256: `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`.
- Extracted ZIP `evidence/` tree Git SHA: `0196e2bc6b207b8065f50698273db9581ca3f286`, equal to GitHub `resources/evidence` tree (all 42 underlying evidence files, path names and bytes).
- All four other original files (`START_HERE.md`, `acceptance.json`, `candidate.template.json`, `verify.py`) match the live Git blob IDs. Reusable checked comparator: `work/h17_source_integrity.py`.
- ZIP's untouched verifier still gives six PASS, K04/K08 MISSING, combined INCOMPLETE.

**Implication:** This uploaded ZIP is **not** a newer source release with hidden target bytes relative to the repo's existing evidence. It does not independently authenticate K04's disputed ACK payload or supply verbatim K08 final words. Target-information intake must seek a genuinely separate witness; please avoid reprocessing identical exports as if they offered new coupon/caption evidence.

Full reproducible summary: [results/h17-attached-zip-integrity.md](../../results/h17-attached-zip-integrity.md). This does not establish that the upstream export was originally complete.

**Current status:** six/8; no new selected coupon bits or exact final-caption words.
