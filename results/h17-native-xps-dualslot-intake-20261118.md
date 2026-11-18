# H-17 native XPS/OXPS print-package recovery intake

**Agent 3 | 18 November 2026 | Implemented and tested. Original K04/K08 remain missing.**

## Recovery mechanism

A preserved Windows print-host artifact may contain an XPS/OXPS ZIP/OPC print package instead of an EMF-record page. XML FixedPage elements can contain text in Glyphs UnicodeString attributes. The original incident archive has no XPS/OXPS source or native spool image. This adds an acquisition path for an **authorized additional source**.

The bounded [XPS parser](../work/h17_xps_text.py) looks for XPS and OpenXPS FixedPage parts, emits per-page joined, spaced and line-separated UnicodeString variants, and can assemble a complete 32-hex coupon or a whole caption from separate glyph runs. It is not a visual renderer.

It was integrated with the *unchanged* archival acceptance rules:

- [K04 source scanner](../work/h17_k04_binary_window_intake.py): scan recovered XPS page text for complete raw 16-byte or 32-hex coupon candidates, with a bounded grouped-hex normalization. Compare each after the original XOR route mask with the original full K04 SHA-256 commitment.
- [K08 profile scanner](../work/h17_profile_k08_phrase_scan.py): pass recovered text to the original normalized-phrase HMAC-SHA256 and K08 SHA-256 commitment path.
- [Profile inventory](../work/h17_profile_inventory.py): classify native .xps and .oxps print files.

The parser requires an OPC package, including ZIP content after a short (at most 4 KiB) native spool preamble. It permits both official FixedPage namespaces, bounds page size at 4 MiB and all pages at 32 MiB, caps pages at 4,096, and rejects DTD/entity markers and unsupported XML roots. It does not decode bitmap glyphs, outlines, glyph IDs without UnicodeString, proprietary non-OPC spool framing, or print order across pages. Joined run variants are candidate-generation hypotheses; only original acceptance can approve any proposed K04/K08 component.

## Positive and negative controls

The [dual-slot SFT](../work/test_h17_xps_text.py) generates a synthetic two-page OPC ZIP.

1. Page one contains a synthetic 16-byte coupon represented as two separate 16-hex Glyphs runs. The **existing K04 source scanner** discovers the complete candidate after joining the runs and passes its full SHA-256 with the original route-mask reducer.
2. Page two contains an entire synthetic late-watch caption split across glyph runs. The **existing K08 profile scanner** matches the planted exact normalized caption using the original desk nonce, HMAC, and SHA-256 commitment path. The source package is byte-identical afterward.
3. Negative controls reject ordinary ZIP without OPC metadata, wrong namespace, truncated XML, DTD, oversized inflated page, and nonpackage input.

The standalone parser's eight regression groups passed locally, including ZIP after a synthetic spool preamble. Full end-to-end integration and the existing scanner self-tests all completed **SUCCESS** in [GitHub Actions run 44244205543](https://github.com/FlareZ123/workplace-v2/actions/runs/44244205543). The extended original K04 acceptance path for a prefix-wrapped synthetic spool file also passed in [GitHub Actions run 44244769617](https://github.com/FlareZ123/workplace-v2/actions/runs/44244769617), commit 3c0da666b32d63c30299051bd5cd8a045cb6a728. The [bounded regression workflow](../.github/workflows/agent3-xps-intake.yml) was then made manual-only to avoid repeated routine CI. The ECMA OpenXPS-namespace and XML-escaped UnicodeString control also **passed** on the manually dispatched current-head [run 44245270747](https://github.com/FlareZ123/workplace-v2/actions/runs/44245270747), which re-exercised both original K04/K08 intake gates and their existing self-tests.

Microsoft documents the [Glyphs UnicodeString XPS field](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/xpsanalyzer-rules) and the [XPS printing path](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/documents/printing-overview).

## Source boundary and next action

The uploaded H-17 export has 56 ZIP members, **zero native .xps/.oxps/.spl/.shd/.prn/.emf/.fpage files**. Exact K04 coupon bytes and Emily's final K08 inscription are still absent. If an original authorized print-host archive or preserved caption-bearing source becomes available, apply the parsers and exact commitment gates. The official original routing/acceptance/verifier, canonical candidate, and already accepted six slots remain unchanged.

**Original state:** K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING, REC8/1 INCOMPLETE.


## Follow-up: glyph-index-only FixedPage text

Agent35 added a complementary helper for the remaining text-extraction gap: XPS/OXPS `Glyphs` elements with `Indices` but no `UnicodeString`. See [`work/h17_xps_glyph_indices.py`](../work/h17_xps_glyph_indices.py) and [its synthetic tests](../work/test_h17_xps_glyph_indices.py). The helper:

- discovers OPC-declared FixedPage parts, including non-`.fpage` names;
- resolves `FontUri` and deobfuscates GUID-named `.odttf` resources;
- maps glyph IDs through cmap, with a conservative Adobe/uni glyph-name fallback when cmap is absent;
- emits per-page lines/spaced/joined streams and coordinate-sorted streams when run coordinates permit;
- leaves ambiguous cmap mappings and non-one-to-one clusters unresolved, with bounded ZIP/XML/font/glyph resource limits.

Eleven synthetic tests pass locally, including an obfuscated embedded font, a cmap-less subset-font fixture, a non-`.fpage` OPC page, relative font URI, multi-run spatial ordering, and the GUID byte-order vector. This helper is **not yet integrated** into `h17_xps_text.py` or the K04/K08 scanner entry points; Agent3 owns integration and Agent20 has been asked to review it. It is an intake capability only: the current export still contains no XPS/OXPS package, and no K04/K08 candidate or commitment result changed.


The helper now also exposes `extract_xps_glyph_streams(data)`, returning per-page `(label, UTF-8 bytes)` variants compatible with the existing `extract_xps_text()` interface. A synthetic reversed-XML-order multi-run page verifies that the coordinate-sorted stream reconstructs the phrase. The local helper suite is now **12/12 PASS**. Integration into the original scanner entry points remains pending Agent3's ownership; no XPS/OXPS source or incident candidate is present.
