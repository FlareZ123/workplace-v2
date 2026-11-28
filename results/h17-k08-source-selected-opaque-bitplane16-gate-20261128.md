# K08: source-selected raw note LOW-BIT as opaque 16-byte component, not text

**Agent 11 | 28 November 2026 | alternate target-reaching mechanism | original K08 commitment 0/56,640 complete checks**

## The new recovery question

Prior target-blind [N20 low-bit MHI selection](h17-k08-n20-rawbody-mhi-three-note-gate-20261128.md) establishes a deterministic three-byte raw-character parity channel: the first 24 original post-label characters of Emily's N20 emit literal `MHI`, naming N13/N08/N09. [Agent11's narrower check](h17-k08-mhi-selected-direct-bitstream-gate-20261128.md) packed all three original selected note bodies as complete eight-bit character streams and found zero valid UTF-8 **plaintext captions** in six immediate interpretations.

A genuinely different route is that **the same parity channel carries a binary 16-byte K08 component directly**. The archive verifier checks a SHA256 commitment of the eventual 16 bytes; a separately recovered exact binary component would validate even if the original normalized caption could not be reconstructed. That is a speculative alternative to the assumption that all recovery work must guess literal final wording. It is **not** an authenticated original key-preimage encoding: source notes do not say Emily stored an HMAC fingerprint in parity bits.

The new test does not require readable ASCII or sentence grammar. It decodes every complete 128-character window of a fixed source-local raw note stream as **128 raw bits**, tests all eight source-character bit planes (with plane0 the independently established LOW BIT), bit0/bit7 first packing, forward/reverse byte order, and checks the resulting entire 16-byte binary output against the **unchanged original K08 SHA256 commitment**.

## Frozen source chains and finite envelope

Five record sequences were selected from already published **target-blind** note/role paths rather than searching arbitrary 24-note permutations:

- N20 itself (the unique independent `MHI` first-24-character emitter);
- MHI's ordered N13/N08/N09 notes;
- First draft N02 → Second draft N06 → selected N01 photograph;
- Version path N02 → N06 → N03 → N13 → N23 final-margin witness;
- N20 → N09, the original note and its source-selected N09 AES/SHA/AES operator.

For a multi-note chain, use the entire original **post-label body**, joined without any new character, with a space, or with a newline at each boundary. Every 128-character consecutive window at each offset is packed under **8 planes × 2 bit-packing directions × 2 byte directions = 32** fixed serialization views. There are no free seed, shift, source fragment cut, alphabet substitutions or selected nonce. The ranges are complete and produce **56,640 original full-component assignment comparisons** (duplicates between modes are not misreported as unique).

| Fixed source chain | Complete 16-byte original commitment checks | Original K08 SHA matches |
| --- | ---: | ---: |
| N20 direct | 1,344 | 0 |
| MHI N13/N08/N09 | 12,416 | 0 |
| N02/N06/N01 | 5,696 | 0 |
| N02/N06/N03/N13/N23 | 29,344 | 0 |
| N20/N09 | 7,840 | 0 |
| **Total** | **56,640** | **0** |

There are 24 original note bodies, but only the above five independently selected complete sequences qualify for this exact hypothesis; arbitrary note chains and cryptographic encoding variants are **outside** the tested model.

## Independent controls and actual result

The program pins the complete original crew SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, source-checks the original `MHI` first24 low-bit signal, and verifies the independently fixed P20 SHA256 `4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c`. It then reads the original `acceptance.json` K08 commitment for the complete binary checks only, never K08 text guesses or the desk nonce.

Two positive controls are deliberately **not** original key recoveries:
1. An independently prepared literal **16-byte synthetic opaque block** is encoded as parity-bearing ASCII and recovered bit-exactly, verifying bit plane, bit packing, byte assembly and payload width.
2. The first 128-character MHI source stream under the frozen original LSB-first packing supplies a planted **synthetic SHA256 target**. The complete original-stream test finds this plant **exactly once**, proving that the enumerator does not omit an in-family carrier and that full16 SHA256 checks work.

Local original-source aggregate output:

```text
source_sha=PASS MHI=PASS P20=PASS
synthetic_full_opaque_digest=PASS
full_component_assignment_checks=56640
planted_original_stream_control_hits=1
original_K08_commitment_hits=0
```

Local elapsed ~1.7 seconds. No original candidate component bytes, source text, original target digest or internal cryptographic state were printed, published or written to public CI. No evidence, acceptance, verifier, canonical candidate or restricted BX25-08 PDF was modified or read.

## Decision and limitations

The preserved note chains **do not directly carry the authentic 16-byte K08 component** as an unmodified contiguous raw-character bit-plane stream under these three separators and 32 simple bit/byte serialization views. The prior plaintext check and the current **opaque component** test are materially different: raw binary K08 preimage bytes do not need to be UTF8 or human-readable.

This does not exclude transposition, scrambling, encryption, nonconsecutive bit selection, error correction, added/removed source characters, a separate physical carrier, or a complete phrase naturally authored but unquoted in the export. It does not prove the source's `MHI` byte was deliberately encoded or that K08 should bypass final wording.

**K08 remains MISSING; K04 remains MISSING; all other six original slots PASS; combined REC8/1 INCOMPLETE.** To reopen this approach credibly, find a source-selected binary payload transform that predicts an entire independent known note/codeword before evaluating K08, not arbitrary bit-order/offset expansion.

## Reproducer

[`agents/agent11/k08_source_selected_opaque_bitplane16_sft.py`](../agents/agent11/k08_source_selected_opaque_bitplane16_sft.py), Python standard library, invoke with the original extracted archive root. Test outputs only aggregates and confirms the exact planned denominator and one in-stream positive.
