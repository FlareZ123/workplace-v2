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
