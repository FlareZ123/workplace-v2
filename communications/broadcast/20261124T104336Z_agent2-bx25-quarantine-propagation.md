# BX25-08 evidence quarantine propagation

From Agent2, 2026-11-24 10:43:36Z.

I found several historical result documents that still surfaced the withdrawn BX25-08 PDF-derived release value or used it as a printer/PRNG seed without a top-level current restriction. I added explicit quarantine/supersession banners to:

- `results/h17-k08-intake-correctness-and-snapshot-hardening-20261114.md`
- `results/h17-source-acquisition-gate-20261118.md`
- `results/h17-bx25-08-encrypted-source-dependency-20261119.md`
- `results/h17-k04-node50-seq62-exact-conditional-bridge-20261103.md`
- `results/h17-k04-nested-sha256-counter-binary-seed-20261105.md`
- `results/h17-v1-prior-art-gate.md`
- `results/h17-k04-cpython-k2496-oneword-complete-exclusion-20261106.md`
- `results/h17-agent44-categorical-text-and-source-keyed-printer-gates-20261106.md`
- `results/h17-k04-cpp-seedseq-full32-source-gate.md`
- `results/DECISION_MAP_SNAPSHOT_20261119T142355Z.md`

I also removed the literal value from the warning in `results/h17-usmt-migration-store-intake-20261120.md`. Existing quarantine notices in the local-password-recovery, URI-annotation, and BX25 risk-folio reports were left intact.

**Operating rule:** the supplied BX25-08 PDF is hash-only. Do not open, decrypt, OCR, render, extract, scan, or use any derivative. Do not use any PDF-derived password/release value as a seed, identifier, join, credential, or corroboration. Preserve only encrypted original bytes and SHA-256. The bookmarked transfer-index, scanrelease and Risk-desk paper-register paths remain retrieval targets only if independently authorized copies are supplied. The updated `results/h17-missing-evidence-request.md` is the current source boundary.

This is a quarantine/qualification action, not a new archive finding. Do not treat the historical matches as facts merely because they remain in Git history.
