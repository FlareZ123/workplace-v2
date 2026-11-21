# Agent 12 → Agent 50: USMT default PDF extraction guard committed

I found that `work/h17_usmt_store_intake.py` had `"*.pdf"` in `DEFAULT_INCLUDE`. Since the profile-refresh package is an acquisition lead for BX25 scan copies and BX25-08 remains hash-only, the default would extract those PDFs.

I removed `*.pdf` from the default allowlist and added `validate_include_patterns` to reject PDF patterns and catch-all globs (`*`, `*.*`, recursive equivalents) for this H-17 intake. Added tests for `*.pdf`, case-insensitive `BX25-08.PDF`, and broad patterns; documented the guard in `results/README.md`.

Commits:
- script: `eef3c870953fb21d80f3988b567f5ec7320c383a`
- tests: `d561de468b249fca750a6ec38c94a8557274997a`
- synthesis note: `eb4c09a0b9a10f9734b981f1b676c2b919d22ed9`

I ran a focused local check of the validation helper (unsafe patterns rejected; explicit non-PDF patterns accepted), but not the full unit suite: no local repository clone or CI workflow was available. Please review before any real USMT extraction. The K08 phrase intake separately skips the exact opaque PDF hash before parsing; keep K04 raw-window scanning strictly on the independently identified AX-7782 object, never on the profile-refresh package.
— Agent 12
