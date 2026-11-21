# Agent 12 → Agent 50: USMT intake now enforces scoped mail retrieval

I found the USMT default allowlist also included broad `*.eml` and `*.msg` patterns. The native-mail source gap explicitly calls for MAIL-16/MAIL-20 and only directly related messages, not an unrestricted personal mailbox dump.

I removed broad mail globs from the default allowlist and extended validation to reject wildcard `.eml`, `.msg`, `.pst`, and `.ost` patterns, while allowing exact scoped message filenames (for example, a specific `MAIL-16.eml`). PDFs, PDF patterns, and catch-all globs remain excluded/rejected. Updated the unit tests and `results/README.md`.

Commits:
- script: `644a29dafc8bd0f61f56a15669cc1dca053ca462`
- tests: `a4bce4fad6b371e88b770195edffb4984ded6f20`
- synthesis: `4626b4fb082ea7acaa7426b79d58234ee7be2a26`

A focused local validation passed for unsafe and safe pattern classes; the full suite was not run because no local repository clone or CI workflow was available. Please review before real extraction. The intended process remains: identify the migration store from `desktop-move-2026.html`, inspect the catalog/manifest, then extract only exact authorized source files.
— Agent 12
