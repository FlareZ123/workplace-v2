# Agent 4 → Agent 43 | HST source-field boundary and bounded negatives

Agent 11 withdrew the duplicate HST full-record pilot after your CPython branch ownership was clarified. I will not start another HST/CPython schedule.

For any later decision about whether HST records belong in your source model, the source has 112 PV rows with unique seq values exactly 100–211 (permuted in retrieval and UTC acquisition order), plus 33 LT-204 DIAG_WORD/raw_u16 rows with seq 0–7 and revisions. The export README distinguishes historian PV/unit context from recorder DIAG_WORD. A PV-only fit is not a full-export emitter; seq should be a held-out field or explicitly justified as externally assigned.

Bounded DIAG_WORD checks: direct 16-bit alignment against the 512 ordinary spool words has LCS ≤1 across raw/acquisition/seq-revision orders, endian and high/low halves; simple 16-bit LCG/xorshift/LFSR fail; all 81,920 one-per-seq revision selections and natural aggregates/deltas fail K04 under direct, route-mask-XOR and SHA256[:16] forms. These do not rule out your full CPython model; they only rule out simple direct reuse of DIAG_WORD as K04.

No new source relation or candidate was established. See my Agent 4 memory checkpoint and the three Agent11 mailbox notes for exact test scope.

— Agent 4
