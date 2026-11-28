# K08: MHI-selected direct raw-bit caption channel does not emit readable wording

**Agent 11 · 28 November 2026 · target-blind source-channel discrimination · K08 still MISSING**

## New question

The independently established N20 raw post-label first-24-character `LOW BIT` channel emits `MHI`, interpreted in A1Z26 as the fixed ordered original note triple **N13, N08, N09**. Unlike previous source-word splices, can applying that same *raw-character* channel to the selected notes recover a **complete literal caption** without freely choosing text fragments, words, synonyms or punctuation?

This is a test of a specific **direct binary payload** hypothesis, not of the selected notes' thematic roles and not of encrypted/encoded descendants. It does not assert that Emily used a bit channel.

## Fixed inputs, options and independent control

Only the original note file is read, pinned to SHA-256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. N20's head must emit `MHI` under the source-established first-character-first-as-LSB convention; those exact bytes fix ordered notes 13/08/09. Each selected record is read as its *entire raw post-label body*, without lexical reconstruction.

Packing one raw ASCII low bit per character into eight-bit bytes tests the inherited LSB-first order and its MSB-first counterpart. The only record-boundary ambiguity is joined with no separator, one space or one newline: **3 × 2 = 6 complete byte-stream decodings**. No offset, selected fragment, cipher key, target hash, nonce or alternative note triple is fitted. A separately planted **32-byte fully printable message** round-trips through the encoder and LSB-first decoder, confirming the bit/byte serialization convention.

## Source-only result

| Body boundary | Byte order | Complete output length | ASCII printable bytes | Valid UTF-8? |
| --- | --- | ---: | ---: | --- |
| Contiguous | LSB first | 31 | 11 | No |
| Contiguous | MSB first | 31 | 12 | No |
| Space | LSB first | 32 | 10 | No |
| Space | MSB first | 32 | 13 | No |
| Newline | LSB first | 32 | 10 | No |
| Newline | MSB first | 32 | 13 | No |

**Zero of six** produces a complete valid UTF-8 caption, let alone a normalized English phrase. No commitment candidate is generated and the original K08 nonce, acceptance digest and verifier are deliberately not read. Original K08 acceptance therefore remains MISSING; this is **not** an original-commitment miss count.

## Decision value and limitations

The new MHI-selected three-note chain **does not** simply carry the final keeper caption as an immediately readable, uniformly packed ASCII low-bit bitstream under the source's own 8-bit convention. This closes that entire small **direct, no-cryptography/no-resynchronization** output family and prevents an attractive but unsupported direct-decoder shortcut from being promoted as recovered text.

This result does **not** exclude alternate encoders, later transformations, external author-final versions, or the linguistic/editorial use of N13/N08/N09. It does not adjudicate whether the MHI discovery was intentional. The next useful K08 step still needs a source-selected *full authoring/version operation* (or new original final-word witness), with a complete output tested privately against the unchanged commitment.

## Reproducer

[`agents/agent11/k08_mhi_selected_direct_bitstream_sft.py`](../agents/agent11/k08_mhi_selected_direct_bitstream_sft.py) runs with the original crew-note file path; asserts the original SHA pin, MHI selection, 32-byte positive synthetic control and all six exact measured output lengths/readability counts. Does not read restricted BX25-08 or original K08 acceptance material.
