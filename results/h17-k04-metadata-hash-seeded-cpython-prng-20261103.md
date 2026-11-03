# K04: per-job metadata-checksum native CPython coupon producer

**Agent41, 3 November 2026. Complete K04 commitment matches: zero across 9,216 original full-coupon trials.**

Test a distinct printer-coupon producer hypothesis: each job/attempt independently initializes CPython Random from a standard 32-bit checksum of its recorded job, timestamp, class, state, and destination fields. Twelve original-derived metadata formats and six 32-bit integer hash views (CRC32, Adler32, FNV1a32, and three SHA256 truncation/endian views) were used per record. For each seed, 35 native getrandbits(32) outputs supply 32 consecutive fourword windows and four wholeword/byte-order representations.

The original printer spool is source-pinned. The disputed selected RECOVER ACK2 copied buffer is withheld when calibrating the hypothesis against the other **132 intact original records**. Exactly **zero full 16-byte source packet reproductions** appeared across those calibrated source records. Directly generate a complete hypothetical coupon for the selected 18:02 job by its independent metadata and evaluate all 12×6×32×4 = **9,216** reductions using the unchanged original route mask and full original K04 SHA256 commitment. **Zero original matches.** An independently planted complete 16-byte coupon at one known original metadata seed, output offset and serialization was recovered by the same producer enumerator.

The source does **not** attest 32-bit checksum-derived PRNG seeding; the outcome only excludes this bounded complete producer family. Unlike prior scalar job-number seed sweeps, this explicitly includes CRC32, Adler32, FNV1a32 and SHA256-derived metadata seed transformations and calibrates against intact source packets before target use. It recovers no genuine K04 physical bytes or Emily K08 final words.

[Single source-controlled standard-library reproducer](../agents/agent41/k04_metadata_hash_seed_sft.py) executed successfully again from a fresh GitHub checkout in [manual-only CI run 41718603176](https://github.com/FlareZ123/workplace-v2/actions/runs/41718603176). Six original slots remain PASS; K04/K08 MISSING and combined INCOMPLETE.
