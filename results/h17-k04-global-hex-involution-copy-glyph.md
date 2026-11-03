# K04: whole-coupon involutive hex-glyph copy substitution

**Agent 8, 3 November 2026. Original commitment outcome: NO_MATCH.** The six previously verified components remain accepted; K04 and K08 are still missing.

## Target-facing alternative mechanism

The original crew N22 describes a label printer behaving like a fax, while MAIL-16 warns that its recovered spool ACK does not authenticate the physical payload. A possible copied-media fault is a globally consistent, **involutive hexadecimal glyph transposition**: certain hex character pairs are systematically swapped, with each other character unchanged. Applying the same mapping twice restores every glyph. This allows damage across the entire selected 32-glyph coupon and includes nonlinear digit substitutions.

This differs from [Agent3's invertible GF(2)^4 affine nibble maps](h17-k04-global-affine-nibble-channel.md), [Agent50's limited-global-glyph changes](../agents/agent50/k04_global_hex_glyph_sft.py), and the printer or mask byte-lane/bit-raster permutations. A general alphabet involution need not be a four-bit affine transformation. It is an explicitly speculative copier model, not independently evidenced firmware.

## Frozen enumeration and result

Use the original 3 October ESC-N / PS-261003-0417 / 18:02 UTC / RECOVER / ACK attempt2 copied spool payload:

- Copied payload: \`A9A9DC5731A5E2AE879C47215C2559D5\`
- Route mask: \`8556C8CB6140A7F9A5123AC7571BEE1C\`
- Original K04 SHA256 target: \`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0\`
- Original spool SHA256: \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`

Enumerate every permutation \`f\` of the hexadecimal alphabet satisfying \`f(f(x))=x\` for all 16 symbols. The involution-count recurrence \`a(n)=a(n-1)+(n-1)a(n-2)\` gives **46,206,736** maps at \`n=16\`. Independently compare the original K04 commitment to each of three 16-byte components:

1. \`f(copied_payload) XOR original_mask\`
2. \`copied_payload XOR f(original_mask)\`
3. \`f(copied_payload XOR original_mask)\`

Here \`f\` is applied consistently to all 32 hexadecimal characters before decoding. These represent damage at the copied-buffer, transcribed-mask and post-XOR encoded-component stages.

**Actual local original-target test: 46,206,736 mappings × 3 = 138,620,208 complete assignments; zero original SHA256 matches.** Some maps produce identical candidates because certain glyphs do not occur, so counts are assignments, not distinct candidate strings. A planted nonidentity six-glyph, three-pair involution had SHA256 controls accepted by all three stages (positive assignments **2, 1, 1**, respectively, from equivalent mappings). No original source, original verifier, original acceptance commitment or canonical candidate was changed.

The [standalone C++17/OpenSSL single-file reproducer](../agents/agent8/k04_hex_involution_codec_sft.cpp) pins the source spool SHA, exact selected ACK selector, route mask and commitment before enumeration. The source-equivalent local executable completed the enumeration; the repository-portable version adds evidence file assertions and has not been independently compiled in a fresh GitHub checkout.

## What is excluded

A *single globally consistent pair-swap codebook* applied at any of those three stages cannot produce the missing accepted K04 under the original mask and copied ACK. An arbitrary non-involutive bijective codebook, mixed independent per-position glyph errors, another upstream generator, different historical selector, original physical copy or independently altered mask remains outside this negative. No authentic selected K04 bits are thereby learned.

This is one finite copy-channel hypothesis rather than a general proof that the missing coupon cannot be reconstructed. K08 terminal final words are still unobserved, and combined REC8 acceptance remains INCOMPLETE.


## 3 November extension: periodic copier/fax channel (distinct stage model)

Source N22's fax-like printer comment motivates a **repeating channel error** alternative to a consistent hexadecimal codebook. This extension does not suppose a physical fax encoder was actually installed; it tests two precisely bounded, whole-coupon corruption families directly against the unchanged K04 SHA256.

- **Periodic bit XOR:** repeat an arbitrary \`p\`-bit pattern across all 128 copied payload bits for every \`p=1..24\`, in both within-byte bit orientations. The payload, route-mask and already-XOR-reduced component stages are mathematically identical for an XOR error, so each distinct stage is counted **once**, avoiding an artificial three-fold inflation. Exactly \`2 × (2^25−2) = 67,108,860\` complete assignments; **zero original target hits**. An independently planted 17-bit periodic error is recovered by the same bit-pattern construction, with Python independently checking the test-pattern bytes and SHA256 digest.
- **Periodic modular byte addition:** repeat an arbitrary 1-, 2-, or 3-byte offset across all 16 bytes, under \`(byte + offset) mod 256\`. Apply it separately to the copied payload, route mask or already-XOR-reduced component; these nonlinear placement choices do not generally commute. Exactly \`3 × (2^8+2^16+2^24) = 50,529,024\` complete original commitment checks; **zero matches**. Source-equivalent local tests reached the complete p1/p2 stages (197,376 assignments) and independently resumed p3 (50,331,648 assignments); a planted payload-stage A5,3C,81 periodic offset was recovered once in p3.

**Total new periodic-channel assignments: 117,637,884; authentic K04 commitment hits: zero.** Counts are assignments with overlaps, not guaranteed unique 16-byte candidates. The two separate local segments returned exact expected counts and original target zero; the bit synthetic was independently checked at its planted member, while a full unsegmented fresh repository execution is not claimed. See the portable [C++17/OpenSSL one-file SFT](../agents/agent8/k04_periodic_copy_channel_sft.cpp), which pins the original spool SHA256, exact selected job, original mask and full commitment, and supports a standalone \`BYTE3_ONLY=1\` repeat of the 50,331,648-addition stage. The code uses \`unsigned __int128\` and therefore requires GCC or Clang, including MinGW/Clang builds on Windows, rather than MSVC.

This is distinct from Agent25's **bit permutations/raster scan geometry**, Agent3's **one arbitrary bitplane** and Agent4's **four-buffer bitplane mosaic**. A repeated XOR pattern may change many bit positions across all byte lanes, and periodic addition allows byte carries. The original artifacts give no independent known-corrupt→known-good copy pair, so the negative is limited to these precise corruption models. Authentic K04 selected bytes remain unobserved, K08 final inscription remains unquoted, and six accepted slots plus two missing remain the official result.
