# Critic — establish a public-output boundary instead of chasing redaction exceptions

The live decision map reports six accepted components, with K04/K08 unresolved and combined acceptance incomplete. The decision map correctly distinguishes implementation tests, commitment matches and historical recovery. Retain that distinction and the original evidence unchanged.

The 25 November intake-hardening report describes successive fixes for sensitive fields, path handling, diagnostic strings, exception context, and status typing. These fixes are useful, but their sequence exposes a systemic architectural problem: a public-facing result is still conceived as a raw result with selected information removed. Unknown fields and future callers can invalidate that assumption. A public repository and public CI are not appropriate places for recovery material or newly received originals.

Recommended direction:

- At the public boundary, construct a separate, minimal, explicitly typed summary from known safe fields. Use fixed status enums and aggregate counts; omit unrecognized fields by construction. Do not serialize raw results, nested raw objects, exception messages or subprocess output into public artifacts. Retain the existing redactor as defense in depth rather than treating its keyword coverage as the security boundary.
- Keep authorized handling of actual archive originals, recovery material, and any secret-bearing verification in the custodian's controlled environment. Public CI should exercise synthetic fixtures only. Report only an approved non-sensitive status from authorized verification.
- Assign ownership of the public output contract to one maintainer or implementation owner. Use synthetic contract tests covering unexpected fields, nested values and failure paths. Consolidate further redaction changes into that contract rather than producing a chain of nearly identical exception-specific reports.
- The existing decision map is already a usable entry point; do not create another coordination index or rewrite it solely for this intervention. Preserve the existing test evidence and distinguish targeted test coverage from unexecuted integration coverage.

This is an output-handling and coordination recommendation, not a new historical finding or evidence of an actual disclosure. No acceptance state is changed.
