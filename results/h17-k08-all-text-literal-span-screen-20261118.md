# K08 exact contiguous-span screen across the text-readable export

**Agent 10 — 17 November 2026**

## Question

Does the accepted K08 commitment correspond to any complete contiguous phrase already present verbatim in the supplied text-readable evidence, including email bodies that were not included in the earlier note-and-galley span screen?

## Method

Used the exact REC8/1 route:

1. Read the K08 desk nonce from `evidence/recovery-routing.json`.
2. Normalize each source file by lowercasing, replacing every character outside ASCII `a-z`, `0-9`, and whitespace with a space, then collapsing whitespace.
3. Enumerate every contiguous normalized word span of length 1 through 128, independently within each file.
4. Compute `HMAC-SHA256(key=desk_nonce, message=normalized_span)`, retain the first 16 bytes, and compare SHA-256 of those 16 bytes with the immutable K08 slot commitment in `acceptance.json`.

The scan covered **41 text files**: all 40 text-readable files under the 42-file evidence tree, plus the supplied `START_HERE.md`. It included all 20 `.eml` files, the mail index, the full noticeboard/desk-note text, the galley log, print-spool text, maintenance logs, HTML, CSV, JSON/JSONL, and procedure text.

The supplied ZIP's 42 evidence files match the repository's `resources/evidence` Git blob identities **42/42**. The ZIP's `acceptance.json`, `candidate.template.json`, and `verify.py` also match the repository's resource files exactly. This establishes that the local scan used the same evidence and acceptance target as the repository.

Reproducer: `agents/agent10/k08_literal_span_screen.py`. It runs against `resources` by default, or the supplied archive root via `--root`.

## Result

<badge color="red">No exact match</badge>

- Text files scanned: **41**
- Normalized tokens: **16,626**
- Contiguous candidate spans tested (1–128 words): **1,801,451**
- K08 commitment matches: **0**

This closes the direct-literal-span gap for all email bodies and the remaining text-readable export. It does **not** test non-contiguous assembly, editorial transforms, OCR/image content, or external source objects. The encrypted `BX25-08.pdf` and binary `trip-recorder.raw` were deliberately excluded; no PDF decryption or protected-source access was performed.

## Implication

A K08 solution must not be claimed by quoting a complete contiguous phrase from the current text-readable export. Further progress needs a source-grounded assembly/version selector or an independently authorized original carrier (for example, the actual envelope caption or its authenticated source image), not another sweep of already-exported literal text.
