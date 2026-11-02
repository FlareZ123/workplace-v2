# K04: full 2^32 legacy MT19937 single-seed producer exclusion

**Agent 1 | 2 November 2026 | Complete original-intact-source exclusion in a narrowly specified seeded-producer class.** The selected K04 coupon and acceptance hash are excluded from all tests.

## Model and distinction

Previous p951 studies inverted CPython `random.Random` / `init_by_array` variable-length keys under speculative output index mappings. This test instead considers the **different native MT19937 single-uint32 initializer**, used by C++ `std::mt19937(seed)` and legacy NumPy `RandomState(seed)`. In contrast to modern `numpy.random.MT19937(seed)`, legacy `RandomState` uses a different initialization algorithm ([NumPy official documentation](https://numpy.org/doc/1.24/reference/random/legacy.html)).

Hypothesis: a single uint32 seed initialized the archive's printer producer; the original first intact printer packet, at hypothetical stream start index zero, consists of four consecutive 32-bit generator outputs. This is a complete generator test that **would** reconstruct the selected K04 packet from a surviving seed and the hypothesized p951 chronology. Neither a hardware producer nor its initial stream phase is historically authenticated.

## Exhaustive source-only experiment

Original source `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Withheld entire selected packet row129. First intact row's 16-byte value is `FBBBC54356483F5864BB3F06794518A5`.

- Enumerated **every integer seed 0..4294967295**, no gaps or duplicates, in 17 disjoint numerical subranges.
- Computed the native MT19937 initial state recursively through word397, its first twist and standard temper; a vectorized AVX2 C++ implementation matches independent `std::mt19937` reference values for seeds 0,1,12345,2147483647,4294967295, including a near-wrap seed. Four 32-bit output words were independently generated for every first-word hit.
- Compared both first-word byte orientations (little-endian 0x43C5BBFB, big-endian 0xFBBBC543), requiring exact 16-byte packet agreement for acceptance.

**Precisely four first-word matches across the entire space:** little endian seeds `1721610931`, `2252269964`, `2967042491`; big endian seed `2900081667`. The four corresponding second raw output words are respectively `82A589D9`, `AB0B8BD2`, `010DC99A`, and `829C253E`. None equals the second intact spool output in the relevant byte orientation, so **zero complete 16-byte packet matches**.

The scan includes **2 × 2^32 first-word comparisons** and four complete four-word comparisons. There is no source-selected seed left inside this entire original-native-seed, first-output model. A seed-based derivation from this model therefore cannot reconstruct K04.

## Reproduction and scope

Local read-only C++17 AVX2/OpenMP SFT `h17_mt19937_single_uint32_seed_search.cpp` enumerates a user-selected half-open interval of 32-bit seeds, checks the five planted native `std::mt19937` outputs and prints all first-word collisions with four generated words. The complete scan used consecutive subranges covering [0,4294967296), including the terminal shorter subrange. Original acceptance and selected packet are never loaded by the SFT. The source script was preserved in the current invocation's downloadable artifacts, not committed remotely.

This exhausts only native **single-integer seeded MT19937 where printer row0 corresponds to generator output0**. Unknown epoch, skipped output prefix, per-event reseeding, CPython seed-array init, NumPy SeedSequence init, or other producer families remain outside. This result cannot authenticate a copied selected coupon, and **no new K04 target bit** is recovered. K08 remains unquoted; REC8 stays six verified components and incomplete.
