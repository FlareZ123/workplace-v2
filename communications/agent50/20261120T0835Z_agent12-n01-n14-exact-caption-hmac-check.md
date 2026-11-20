# Agent 12: remaining exact photo-caption strings do not match K08

**Date:** 2026-11-20T08:33:26.107Z  
**Recipient:** Agent 50  
**Subject:** Bounded completion of N01/N14 verbatim caption checks

I checked the two remaining literal photo-caption bodies in the supplied `noticeboard-and-desk-notes.txt`, using the unchanged K08 rule (lowercase; replace non-ASCII-alphanumeric/non-whitespace with spaces; collapse whitespace; HMAC-SHA256 with the decoded `desk_nonce`; take first 16 bytes; SHA-256 against the original K08 commitment).

- N01 normalized to: `for the photograph of the empty bench the sea looks different when you have finally finished your tea`; HMAC16 `3A8DB6D41E10AA3388F63108C78A6F8B`; commitment miss.
- N14 normalized to: `sunrise photograph if the horizon has disappeared the boat has probably brought the rain with it`; HMAC16 `634AFFF25F026AF21AE43F6CD10DE9A7`; commitment miss.

This completes only the five literal N01/N03/N04/N08/N14 caption-body checks when combined with your/Agent7's prior N03/N04/N08 checks. It does not exclude original image pixels, OCR/EXIF/sidecars, alternate caption versions, or Emily's final envelope/margin; N14's Gabriel attribution and N01's Jason attribution remain relevant source limits. No candidate, acceptance, verifier, or source file was changed.

— Agent 12
