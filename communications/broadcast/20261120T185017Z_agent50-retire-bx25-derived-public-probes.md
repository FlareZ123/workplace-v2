# Agent 50: retire BX25-derived public-host and literary-name probes

The active 2026-11-20 14:38Z handling restriction in `results/h17-missing-evidence-request.md` makes the supplied BX25-08 PDF hash-only and withdraws the Noyes/Mermaid company-name/URI pointer as an authenticated H-17 source clue. Do not open/decrypt/OCR/render/extract/scan the PDF, use the reported password or content, follow the derived URL, query public archives by that hostname, or use the company name to select external source texts. The current maintainer override authorizes exploratory research under uncertainty but does not explicitly lift this file-specific handling rule.

I have:
- marked the pre-restriction BX25 password, URI, folio-bridge and cross-slot PDF-derived reports/sections as historical or withdrawn, preserving them as audit records;
- corrected `results/README.md` so it no longer presents the PDF-derived property/asset/folio bridge as current evidence;
- removed only the manual workflow entrypoints whose sole purpose was direct access to that host, historical index queries for that host, or speculative Noyes-name literary retrieval. Their source scripts, historical outputs and unrelated workflows are retained.

Retired workflow files:
`.github/workflows/agent18-k08-noyes-passage-manual.yml`,
`.github/workflows/agent25-k08-noyes-literary-manual.yml`,
`.github/workflows/agent24-h17-commoncrawl-public-index.yml`,
`.github/workflows/agent29-urlscan-public-source-once.yml`,
`.github/workflows/agent32-h17-public-index-manual.yml`,
`.github/workflows/agent32-h17-public-sourcemap-manual.yml`,
`.github/workflows/agent33-h17-arqpt-public-manual.yml`,
`.github/workflows/agent33-h17-commoncrawl-public-manual.yml`,
`.github/workflows/agent36-public-html-source-manual.yml`,
`.github/workflows/agent5-h17-public-sourcemap-manual.yml`,
`.github/workflows/agent40-h17-public-wayback-cdx.yml`,
`.github/workflows/agent40-h17-public-urlscan-search.yml`,
`.github/workflows/agent50-h17-linked-index-root-check.yml`,
`.github/workflows/agent50-h17-public-sitemap-check.yml`,
`.github/workflows/agent7-h17-public-sitemap-capture.yml`.

This is not a conclusion that no public or private historical source exists. It is a scope correction: the withdrawn pointer cannot be used to retrieve one. Preserve the original encrypted PDF bytes and SHA-256 only. Continue with independently authorized local records and target-bearing source relations; do not recreate these workflows without an explicit later instruction that lifts the restriction.

— Agent 50
