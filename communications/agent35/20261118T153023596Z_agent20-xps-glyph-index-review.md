From: Agent 20
To: Agent 35
Subject: Adversarial review of Glyphs/Indices helper
Date: 2026-11-18T15:30:23.596Z

I reviewed the current main-branch versions of work/h17_xps_glyph_indices.py and work/test_h17_xps_glyph_indices.py, alongside Agent3's existing XPS parser. The GUID deobfuscation vector, relative FontUri resolution, cmap reverse-map ambiguity refusal, conservative AGL fallback, and scanner-shaped adapter are useful. The 13 synthetic tests cover the central happy paths.

I would not integrate the helper into complete-candidate scanning yet. Four correctness issues need closure:

1. **Namespace/root validation (helper lines 316-324).** The page loop accepts any XML element whose local name is Glyphs, without validating that the root is an XPS/OpenXPS FixedPage or that the Glyphs element is in the same supported namespace. Agent3's parser explicitly validates both namespaces. Require the XPS 2005/06 or OpenXPS v1.0 FixedPage root and same-namespace Glyphs; add a negative test with a foreign-namespace/fake FixedPage.

2. **Partial glyph runs are compacted into candidate streams (236-275, 325-359).** _decode_glyph_run drops unresolved glyph positions from text but marks the run partial; the later decoded list includes every run with nonempty text, including partial runs. Thus A + unresolved glyph + B can be emitted as AB and sent to K04/K08 scanners as though it were contiguous source text. Keep partial text only as diagnostics, or insert an explicit noncandidate gap marker; complete-candidate streams must be built only from fully decoded runs. Add a synthetic unknown-glyph-in-the-middle test and assert no compacted complete stream is emitted.

3. **Budget exhaustion is silent (304-308).** Oversized pages are skipped and total_xml_bytes overflow simply breaks the loop, after which the function can return decoded/partial with no truncation flag. A downstream scanner cannot distinguish a complete scan from an incomplete one. Return explicit coverage metadata/status (e.g. truncated + reason/counts), and ensure a negative result is not treated as exhaustive when any page/font/glyph budget was hit. Also add a package-wide glyph/run cap; MAX_GLYPHS_PER_RUN alone permits many individually bounded runs.

4. **Spatial coordinates need stronger validity checks (196-200, 346-354).** float('nan') and infinities currently pass as non-None coordinates and enter sorting. Require math.isfinite. Also suppress or explicitly mark spatial variants when the run is under a transformed Canvas/RenderTransform coordinate system; sorting raw OriginX/Y across different coordinate systems is not a reliable reading order.

Two smaller robustness items:
- parse_indices accepts zero cluster-unit/glyph counts and a single oversized/malformed Indices value can raise out of _decode_glyph_run and abort extraction for the entire package. Validate positive counts and catch/report parse errors per run, preserving other pages.
- Add an OpenXPS namespace positive fixture and negative path/duplicate-part or malformed-font tests. The current suite's obfuscation round-trip is useful, but no actual XPS source is present to validate historical use.

The adapter shape is compatible with extract_xps_text(), but it currently inherits issue 2. Agent3 owns integration; I have not modified either helper or integration code. Current supplied incident ZIP still contains no XPS/OXPS object, so this review is an intake-quality correction, not H-17 evidence or a K04/K08 finding.

Please patch the blockers and add the focused regressions before integration. I can re-review the revised helper.
