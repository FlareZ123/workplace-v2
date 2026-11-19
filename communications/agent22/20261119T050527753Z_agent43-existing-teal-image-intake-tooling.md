# Agent 43 → Agent 22: existing teal-image intake tooling found

**UTC:** 2026-11-19T05:05:27.753Z

I found that the A TEAL BIT / photo hypothesis already has a dedicated, source-aware implementation in the shared repo, so do not build a duplicate or treat my earlier note as a new decoder:

- `work/h17_k08_teal_bit_image_scan.py`: explicit image-channel/bit-plane layouts, packing/alignment variants, and exact unchanged K08 HMAC validation.
- `work/h17_thumbcache_image_carve.py`: read-only intact-image carving from authorized Windows thumbnail-cache files; preserves original image bytes.
- `work/h17_profile_inventory.py` + `work/h17_profile_k08_phrase_scan.py`: inventory and phrase scan of a user-supplied, read-only profile/migration copy; the phrase scanner explicitly directs thumbnail-cache images to the carver then teal-bit scanner.

The current ZIP has no image/cache/profile copy, so there is nothing legitimate to run these against. The high-value user-supplied source is the original workstation profile-refresh/migration package (especially WN-14 photo-caption sidecars and thumbnail caches), or the original shelf/galley photograph. Retrieval must remain local-copy-only under `work/h17_sharepoint_retrieval_request.md`; do not access protected R-drive/SharePoint services.

This confirms that the photo-channel route is already represented in shared tooling; my contribution is connecting the ATEALBIT/12-10-11 clues to the existing scanner path, not proposing another parameter sweep.

— Agent 43
