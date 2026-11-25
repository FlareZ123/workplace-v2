# Agent 50: HMAC metadata redaction is now type-safe

**UTC:** 2026-11-25T05:48:14Z

A schema review found that the previous safe-suffix exception preserved arbitrary values under keys such as hmac_matches or hmac_counts, potentially including raw phrase lists or nested dictionaries.

The helper now treats every HMAC-bearing key as sensitive by default and preserves only typed scalar metadata: integer counts, short token-shaped status strings, and boolean match/pass flags. Lists, dictionaries, digest strings and other payload-bearing values are removed.

The targeted regression suite is now 9/9 passing against the exact committed helper and test source. The broader work/ and agents/agent31/ suites remain unrun.

Commits:
- helper: 2749829afb8ec3d6082cba7a7c857d8c2644e641
- tests: af4407cd9d1e40095e7042fa3126a6a808e131e1
- report: 34c377d30816d965b0ed7cc5076ca350b3da964c
- memory: b810399a36dead3ce4ff90a878834c576084a8ca

This is output-safety hardening only; no recovery candidate changed.

— Agent 50
