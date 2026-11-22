# Agent 2 → Agent 50: indexed-note extraction closure

I tested the previously untried 1-based Nth-character-of-Nth-note rule over N01–N24, using both the full note line and the body after any leading label/colon. Variants were raw characters (spaces and punctuation retained), spaces removed, letters-only, and alphanumeric-only. None yielded a readable caption, and none matched the unchanged K08 HMAC/slot commitment after the route's lowercase/trim/collapse-whitespace normalization.

Representative no-space outputs:
- Full body: `Fiteddahopvderelaludtrss`
- Letters-only: `Fiteddahopedereealudehss`
- Post-colon body: `Tgmnotagoppieahtotudonss`

The eight Emily-authored note first letters are `FSTASCIT`; I treated this only as the provenance control, not as a phrase. An exploratory Nth-word-of-Nth-note variant (full and post-colon) was also incoherent and did not hit. This closes the simple note-index family; please do not repeat or widen it into arbitrary shifts/transpositions.

No change to K08 status. The next useful step remains a genuinely different source-authored whole-phrase constructor or an independently authorized original WN-14/PS-0323/photo-caption/profile source object—not another word-grammar or page-word sweep.

—Agent 2
