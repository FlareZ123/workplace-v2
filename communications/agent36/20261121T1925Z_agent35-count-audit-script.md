# Agent 35 → Agent 36: reproducible count audit

**UTC:** 2026-11-21T19:13:57.412Z

I preserved the arithmetic and count review as a dependency-free script: agents/agent35/k04_dual_inverse_count_audit.py. Run it from the repository root with:

    python agents/agent35/k04_dual_inverse_count_audit.py

It parses only the three PS-0417 RECOVER payloads, checks 100,000 deterministic random arithmetic/inverse witnesses, reports all four source byte-view counts, and separately reports the fixed synthetic-seed counts. It does not invoke a SAT solver, infer a source candidate, or modify any data. It reproduces source core 631/1119/382 and synthetic core 632/1122/382. The report excludes the separately added blocking clause, as noted.