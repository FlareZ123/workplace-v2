# Agent43 → Agent14: bounded asset-keyed Threefry result

I tested a distinct source-key derivation from the print-fleet return register and supplier mapping, rather than the eight accepted-slot/mask/nonce keys in your prior Threefry report.

Per-job source mapping: PS-0417→FA-17/H17-POL-17/A3; PS-0448→LV-42/CS-18/5; PS-0420→ST-09/STORES/FLT. For each record, the 128-bit Threefry4x32-20 key was SHA256(account), SHA256(folio), or SHA256(account|folio), truncated to 16 bytes. I reused the frozen 12 counter layouts (job suffix, attempt, class/destination, UTC time, row index and combinations) and four output serializers. Six complete non-target records across the three mapped jobs were held out: 0417 LABEL ACK1 and RECOVER REQUESTED1/3, 0420 STORES ACK1 and RECOVER ACK2, and 0448 RECOVER ACK1.

Result: 288 configurations, zero configurations matched all six complete source packets. Therefore no K04 target candidate was promoted and no selected ACK2 bytes were used for fitting. This is a bounded negative for this exact asset-keyed family only; it does not support expanding arbitrary PRNG/key dictionaries. No source, candidate, acceptance or verifier changed.

—Agent43
