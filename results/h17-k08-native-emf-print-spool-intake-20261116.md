# H-17 K08: recover exact rendered words from native Windows EMF printer pages

**Agent 23 | 16 November 2026 | bounded acquisition enabler; no original K08 commitment hit.**

## Problem addressed

An authorized original printer host or legacy office-profile export could contain an EMFSPOOL `.SPL` file or standalone `.emf` page bearing literal recovery-envelope or caption text. The existing K08 inventory and exact HMAC scanner accepted printer paths but did not parse the structured vector text records of Windows Enhanced Metafile pages. Raw UTF-16 window decoding can fragment records, mix binary operands with text, or miss a caption stored in multiple separate drawing commands. This implementation extracts complete strings from valid native records and presents page-level joined variants to the unchanged exact K08 reduction.

The *supplied* H-17 ZIP contains the copied 16-byte print ACK log, not an original selected PS-0417 or candidate PS-0323 native spool/rendered page. This work does not add a witness to the export.

## Implementation

- [Native bounded parser](../work/h17_emf_text.py): locate EMR_HEADER via the `0x464D4520` signature; enforce total length, aligned record sizes/count, and terminal EMR_EOF; extract EMR_EXTTEXTOUTA/W, EMR_POLYTEXTOUTA/W, EMR_SMALLTEXTOUT, plus EmfPlusDrawString inside EMR_COMMENT_EMFPLUS. For each complete page emit direct line-separated, space-joined, and unspaced variants. Skip unknown formats and glyph-index or bitmap-only text, requiring a renderer/OCR for such pages.
- [Existing profile inventory](../work/h17_profile_inventory.py): include standalone `.emf` under the already-supported `printer` category. The `.spl`, `.shd`, and `.prn` printer file classes were already included.
- [Existing K08 phrase scanner](../work/h17_profile_k08_phrase_scan.py): for an authorized inventory's printer file with an EMF signature, pass extracted page text through the existing exact candidate-normalization, HMAC-SHA256/first16 and SHA256 acceptance comparison. Other extraction paths and mailbox exclusion remain unchanged.
- [Standalone regression](../work/test_h17_emf_text.py): synthetic two-page EMFSPOOL wrapper; Unicode/ANSI ExtTextOut, PolyTextOut, both SMALLTEXTOUT encodings and rectangle layouts, EMF+ UTF-16 DrawString and malformed record guards; one planted *complete* caption passes the unchanged K08 cryptographic rule. Tests were executed locally on the same source submitted to GitHub: all five printed PASS.

The parser's EMF and EMF+ layouts were checked against Microsoft official [MS-EMF] sections 2.3.3, 2.3.5.7/8/32/33/37 and [MS-EMFPLUS] section 2.3.4.14. It performs no source writes, privileged system access, network retrieval or printer operation.

## Scientific boundary

- **Recovered original final caption:** none.
- **Authentic K08 commitment hits:** none, because no new native printer file was supplied.
- **Synthetic exact positive:** PASS; demonstrates that the parser and HMAC reduction can recover an entirely specified caption if it is present as supported native vector text.
- **Unaddressed input classes:** bitmap-only pages, font-encoded glyph IDs, unsupported EMF+ driver glyph streams, proprietary printer languages and encrypted spool data.

This is a concrete reusable intake improvement for a later authorized original PS-0323/PS-0417 native spool or office-profile image; a source-stage caption relationship to either job remains unproven. It is not a claim about historical K08 text or an accepted seventh component. The six accepted REC8 slots and original candidate, verifier, route and commitments were not modified. Combined REC8/1 remains INCOMPLETE.
