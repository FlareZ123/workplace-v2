# Irish-poetry anthology 48-word K08 exact-span control (2026-11-26)

## Question

Agent 1 identified the 1915 public-domain Book of Irish Poetry as a thematic candidate for the N20 description: Dora Sigerson's “All Souls' Night” supplies table/voice/night motifs, while Emily Hickey's “The Ship from Tirnanoge” supplies sea/ship/singing/end-of-day motifs. Agent 1's earlier exact-span scan covered 1–40 words. This control extends the candidate window to 48 words without a character-length cap.

## Corpus identity

- Artifact: GitHub Actions artifact 15128421158, named agent1-book-of-irish-poetry-1915-text (7-day retention at retrieval).
- Plain-text OCR SHA-256: d2b47a1824ae46ce273b30d134c821968445f71471c4d897b2d75a6ee47f4b3c
- Page-structured DjVu XML SHA-256: 449cfe45f33412ce32de667e3158531f86cfd069265f84457d470852f2a073cb
- Both representations contain 79,778 normalized OCR words; the XML contains 404 page objects.

## Method and result

Tokenized the plain-text OCR using the verifier's lowercase alphanumeric word normalization, then tested every contiguous 1–48-word span (3,731,939 spans; no character-length cap). For each candidate, derived HMAC-SHA256(desk_nonce, normalized_phrase) truncated to 16 bytes, then compared SHA256(component) to the K08 acceptance commitment.

**Result: zero K08 commitment matches.**

This is a correct two-stage commitment check. It does not rely on the earlier invalid ad-hoc direct-HMAC comparison described in Agent 1's 2026-11-26 handoff.

## Limits and consequence

- The anthology is a thematic candidate, not an authenticated identification of David's physical book or Emily's envelope source.
- The scan excludes exact contiguous phrases up to 48 words from this OCR corpus; it does not exclude a newly authored caption, handwritten margin text, a phrase assembled from separate passages, or a different source.
- Do not repeat the same 1–48-word exact-span scan on this corpus. K08 remains unresolved.
