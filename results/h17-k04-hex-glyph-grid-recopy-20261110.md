# K04: independent hexadecimal-glyph 4×8/8×4 copier-grid recapture

**Agent 47 | 10 November 2026 | Original historical commitment: NO_MATCH.** The preserved selected ESC-N/PS-261003-0417 attempt-2 ACK payload is reconstructed from unverified fragments. This is a finite exploration of a possible *character-level* grid/copy-order transformation. No retained document authenticates a 4×8 or 8×4 printed coupon layout.

## Distinct test

Agent6's preceding [4×4 byte-grid study](h17-k04-grid-recopy-original-20261104.md) permuted complete bytes, row/column reversals and bytewise bit/nibble transforms. The present study instead treats the **32 individual hexadecimal characters** as the units of a 4×8 or 8×4 grid, permitting arbitrary global row permutation and arbitrary global column permutation. Either use normal column direction on every row or mirror column order on alternate rows (serpentine line capture). This includes orderings that separate the high and low nibbles of the same original byte.

Input selected copied payload: `A9A9DC5731A5E2AE879C47215C2559D5`. Recorded route mask: `8556C8CB6140A7F9A5123AC7571BEE1C`. Original K04 SHA256 commitment: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Three independent stages receive the grid transform and then an entire 16-byte original commitment check:

1. Reorder copied payload characters, repack to bytes, XOR unchanged mask.
2. Reorder mask characters, repack, XOR unchanged copied payload.
3. XOR original copied payload/mask first, reorder the 32 resulting component hex characters, repack.

For each stage, an independent nonidentity 4×8 planted full-component SHA256 target is recovered exactly once, confirming each end-to-end enumeration and reducer. **The selected ACK2 was deliberately included**, because this experiment concerns correcting its reconstructed copy. The assumption is a pure rearrangement of its characters or the route-mask/component transcription; the source still does not attest that any of these 32 glyphs survived physical copying correctly.

## Completed results

- All 4×8 and 8×4 global row/column permutations, both serpentine directions: **3,870,720 layout assignments**.
- Three complete component checks per layout: **11,612,160** original full SHA256 comparisons.
- Original K04 complete-candidate hits: **0 for each of the three transformation stages**.
- Planted nonidentity whole-coupon positives: **1/1 for each stage**.

Executed the C++17/OpenSSL source-pinned [SFT](../agents/agent47/k04_nibblegrid_sft.cpp) against the unmodified original supplied ZIP extracted to `/mnt/data/h17_archive_local`, which matched the repository evidence. The code checks the original printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, route SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5` and acceptance SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`. Runtime about 5 seconds locally with OpenSSL. `g++ -O3 -std=c++17 ... -lcrypto` is sufficient on a system with the development library.

This excludes the defined hex-glyph grid ordering family, **not** arbitrary 32-nibble permutations, corrupt/missing original hex glyphs, alternate print payload generators, or physical-media copy loss. Original K04 authenticated selected coupon bits remain 0/128; K08 final exact wording remains unknown. Six original slots still pass and combined verification remains incomplete. Continue with different producer/source-output relations rather than multiplying nearby glyph-layout variants.
