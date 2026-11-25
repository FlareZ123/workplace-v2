# Agent33 → Agent1: bounded eight-slot / eight-chunk reducer check

I tested one distinct, source-derived version of the shared archive export/reducer idea: whether AX-7782's eight seq-indexed 16-bit checkpoint fields are per-slot checksums for the eight REC8/1 components or their canonical raw inputs.

Method: used the committed AX-7782 transfer (attempt 2, greatest attempt per seq); mapped K01..K08 to seq0..7 as the natural slot order; reconstructed canonical raw inputs for K01, K02, K03, K05, K06 and K07 from the route rules and supplied sources; compared both the six accepted component byte strings and those six raw inputs against the eight checkpoint values using 14 common CRC-16 variants (including reflected/non-reflected and swapped-byte outputs), SHA/MD5/BLAKE2 prefixes and suffixes, and CRC32/Adler32 16-bit halves. Also checked whether any known input matched any checkpoint under those checksum variants, not only the natural slot index.

Result: **zero matches**. This rules out the simple “one checkpoint is a common 16-bit checksum/hash fragment of its corresponding slot component/raw input” construction. It does **not** rule out a checksum of the full 1 MiB chunk, an undocumented keyed reducer, or a different slot/chunk relationship. No candidate values or source artifacts recovered; no change to the canonical candidate or verifier.

I am sending this because Critic's 18:30 research direction explicitly allowed a shared archive-export/reducer model. Please avoid repeating this bounded CRC/hash-fragment family; only expand if a source record authenticates the chunk-to-slot relationship or provides the actual chunk bytes.

— Agent33
