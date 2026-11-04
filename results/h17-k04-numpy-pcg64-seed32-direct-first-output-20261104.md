# K04: exhaustive direct NumPy PCG64 32-bit-seed source falsifier

**Agent 2 | 4 November 2026.** New, complete source-producer search over the exact 2^32 unsigned scalar seed space. The candidate source model fails its first intact printer packet before constructing a selected K04 coupon. The original six verified slots remain PASS; K04/K08 remain unresolved, combined acceptance is INCOMPLETE.

## Different target-reaching model

A plausible synthetic printer producer is `numpy.random.default_rng(seed).bytes(16)` with a single unsigned 32-bit integer seed and consecutive outputs. Unlike previous CPython MT19937, NumPy MT19937 pool-size or PCG32 brute-force experiments, NumPy's default generator uses **PCG64 XSL-RR 128/64** and a **SeedSequence**-initialized 128-bit state and 128-bit odd increment. This mode was previously left open in Agent 2's memory after a QF_BV inversion on *unknown* 128-bit PCG64 state could not solve a synthetic pair in 12 seconds. This experiment circumvents that nonlinear inversion by enumerating a precisely delimited lower-entropy seed space.

Primary source is the untouched `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. First intact chronological printer packet is PS-261003-0300, ACK/LABEL, 07:00 UTC, payload `FBBBC54356483F5864BB3F06794518A5`. The search does not fit the disputed selected 0417/18:02 ACK2. A genuine continuous PCG64 emitter with this direct start rule **must** produce the first 64-bit row0 word as its very first PRNG output.

NumPy source/API used for the exact implementation:

- [NumPy 2.3 PCG64 documentation](https://numpy.org/doc/2.3/reference/random/bit_generators/pcg64.html), including the SeedSequence-to-PCG64 state rule.
- [NumPy 2.3.5 SeedSequence source](https://github.com/numpy/numpy/blob/v2.3.5/numpy/random/bit_generator.pyx): pool4, 32-bit hashmix, cross-pool mix, and `generate_state(4, uint64)`.
- [NumPy 2.3.5 PCG64 C source](https://github.com/numpy/numpy/blob/v2.3.5/numpy/random/src/pcg64/pcg64.h) and [set-seed mapping](https://github.com/numpy/numpy/blob/v2.3.5/numpy/random/src/pcg64/pcg64.c), including the two initialization advances and next-output advance.

Both full first-64-bit byte orders (little/big endian) are checked. Had either matched, the following raw 64-bit output would have been checked against the second half of the same original packet. The complete original SHA and first full packet are asserted by the final source-pinned test; all surviving printer packets are otherwise withheld.

## Complete executed result

The local optimized C equivalent enumerated every seed in `[0,2^32)` as eight nonoverlapping logical 2^29-wide shards. The last shard was run as two disjoint 2^28 halves after an initial timed-out attempt; only the two completed halves are counted. Every completed range returned **zero matches** to either first 64-bit representation. XOR of each range's computed first raw PRNG outputs provides an inexpensive reproducibility fingerprint.

| Unsigned seed range [start,end) | Count | First-word matches | XOR of first 64-bit outputs |
| --- | ---: | ---: | --- |
| 0..536870912 | 536,870,912 | 0 | `5525291bd4613af1` |
| 536870912..1073741824 | 536,870,912 | 0 | `a4faf328655cdcee` |
| 1073741824..1610612736 | 536,870,912 | 0 | `b19a1ee5cf430f62` |
| 1610612736..2147483648 | 536,870,912 | 0 | `5c02cb416968ce51` |
| 2147483648..2684354560 | 536,870,912 | 0 | `0506dc50d891e1bb` |
| 2684354560..3221225472 | 536,870,912 | 0 | `a72a0b045f18b645` |
| 3221225472..3758096384 | 536,870,912 | 0 | `daa72b5c8c13fb80` |
| 3758096384..4294967296 | 536,870,912 | 0 | `9cf18ce5470b5bbe` |
| **Total** | **4,294,967,296** | **0** | **`f83d7f7a5b87d0ec`** |

**Genuine planted producer positive.** Independently queried NumPy 2.3.5 `PCG64(42)`. Its state `cea44f6798798f2aacbc7c9d68860ac8`, increment `fa505436c9a8416e66caf2e28d25abff`, first outputs `c621fbcd16d92688`, `705a5661a791ffc1`, and `default_rng(42).bytes(16)` `8826d916cdfb21c6c1ff91a761565a70` all independently matched the C implementation. The final source-pinned reproducer also passed the seed42 assertions and its first-million-seed XOR `789103adebc92efc`, identical to the tested full-range implementation's first million.

Reproducer: [Agent 2 single-file C SFT](../agents/agent2/k04_numpy_pcg64_seed32_full_source_sft.c), requires GCC/Clang and OpenSSL libcrypto. Run from repository root in disjoint seed intervals. The original evidence, commitments, verifier and canonical candidate were never edited. The full original-data search was run locally; CI has not independently rerun all eight shards.

## Exact exclusion boundary

Under **first-output, no-skipped-draws, NumPy PCG64, SeedSequence default four-word pool, unsigned scalar 32-bit seed**, no seed generates even the first 64 bits of the original printer's first intact payload in either byte order. Thus this complete finite producer model cannot predict the selected coupon. This result says nothing about 64/128-bit seeds, initial draw skips, file-epoch offsets, distinct PCG64DXSM, switched generator epochs, a different packet emitter, or post-generation copied-payload damage. It does not recover a K04 original bit.

A next PCG64 experiment should establish an independent source-era offset or seed-width mechanism before multiplying exhaustive passes. A stronger breakthrough would predict a *different whole intact packet* and a complete selected coupon under the same source-heldout causal model. The actual K04 physical copier and Emily-final K08 text remain unresolved.
