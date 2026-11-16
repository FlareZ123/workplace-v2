# Agent 1 — K08 thumbnail-cache image intake is available

The existing K08 profile phrase scanner inventories thumbcache_*.db and Thumbs.db but only scans their raw embedded text; it does not decode image payloads. The oldscan/photo and office-profile references make this a plausible carrier gap.

Added:
- work/h17_thumbcache_image_carve.py
- work/test_h17_thumbcache_image_carve.py

The carver is read-only against source files. It extracts intact JPEG, PNG, GIF, BMP and WebP payloads byte-for-byte, validates them, records offsets/dimensions/SHA-256, deduplicates by content hash, and writes only to an output directory outside the source tree. It is deliberately not a full thumbcache/OLE parser: it does not recover original paths or timestamps, and it does not decode TIFF/proprietary payloads. Five synthetic tests pass.

Usage on an authorized read-only retired-profile copy:

    python work/h17_thumbcache_image_carve.py /mnt/read-only-profile --out-dir /tmp/h17-thumbcache-images
    python work/h17_k08_teal_bit_image_scan.py --images /tmp/h17-thumbcache-images/images --resources /path/to/extracted-h17-resources

The supplied ZIP contains no thumbnail-cache files, so this is an intake enabler only, not a K08 recovery. The profile scanner warning and results/README.md now point to the tool. Do not treat the ATEALBIT hypothesis as authenticated.
