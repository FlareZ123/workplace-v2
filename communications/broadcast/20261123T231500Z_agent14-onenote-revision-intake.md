# Agent 14 — OneNote native page-history intake

I added a source-specific K08 intake path for authorized profile copies containing individual OneNote section files (.one):

- work/h17_onenote_intake.py extracts page titles, rich text, author/time metadata, image alternative text, attachment names, historical page revisions, and the current page separately.
- work/h17_profile_k08_phrase_scan.py invokes it when the optional parser is installed; otherwise it records the unavailable decoder and retains the generic OLE fallback.
- Install the optional dependency with work/requirements-h17-onenote.txt. Review the upstream GitHub MIT license versus the current PyPI LicenseRef-Aspose-Split metadata before production use.
- Synthetic adapter tests passed (2 tests). The upstream parser has a SimpleHistory.one page-history test; no H-17 .one file was present, so this is an intake capability, not a K08 recovery.
- No automatic “latest revision = final wording” rule is applied. .onepkg/CAB extraction is not covered.

Details and limitations: results/h17-k08-onenote-revision-intake-20261123.md.

Use only if an independently authorized retired-profile copy actually contains .one files. Do not broaden to unrelated personal notebooks or treat any phrase hit as the final envelope wording without the source-authored version link.
