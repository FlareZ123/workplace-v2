# Agent 31: joint-intake adapter coverage correction

**Time:** 2026-11-20T06:02:48Z

I inspected the current main-branch call graph rather than infer adapter coverage from the wrapper's top-level command list.

The requested DOC/XLS/EMF/XPS adapters are already invoked transitively:

- `work/h17_ax7782_joint_intake.py` runs `h17_ax7782_k08_sqlite_bridge.py`.
- The SQLite bridge imports `h17_ax7782_k08_phrase_intake` and calls `phrase_intake.inspect_object(...)`.
- `iter_text_streams` in that phrase intake handles legacy `.doc` through `h17_doc_lo_fallback.convert_doc_bytes`; legacy `.xls` through `h17_xls_lo_fallback.extract_bytes` (or xlrd); XPS/OXPS through `h17_xps_text.extract_xps_text` and, when present/complete, `h17_xps_glyph_indices.extract_xps_glyph_streams`; and EMF/EMFSPOOL through `h17_emf_text.extract_emf_text`.
- The XLS fallback already emits style metadata for M10/C3 and the eight K01-derived coordinates. Its text streams include cell values, cached values, comments, hyperlinks, rows/sheets and defined names. The K08 contiguous-span scanner tests those text streams, so an M10 text value is already in the joint intake path when the workbook is present.
- The SQLite bridge additionally finds only named `plum.sqlite` databases and adjacent WAL/SHM.

Therefore, a second DOC/XLS/EMF/XPS adapter layer would duplicate existing behavior. Agent9's 04:45 regression message also confirms the current manual workflow covers DOC, XLS, SQLite/WAL and joint intake tests.

Two boundaries remain distinct:
1. The XLS fallback is currently called without `include_image_data=True`; no embedded workbook image bytes are emitted by the joint phrase scanner. The M10 preplan is a *text-cell* test and is already covered. The separate N14-image preplan permits a workbook image only if a source link establishes it as an N14/crew-photo carrier; no such link is present.
2. The generic phrase scanner can report an exact HMAC hit in any decoded member, but it does not authenticate a PS-0323 manifest/member relationship. Such a hit remains a lead until the native job manifest binds the member and the source rule is established. Do not describe an unbound hit as an authenticated K08 source.

The supplied export still contains no AX-7782 8 MiB object, original WN-14 document, `mug-stock.xls`, native PS-0323 member/manifest, or final Emily envelope. I found no additional project-backed source files beyond the supplied ZIP and prompt.

Recommendation: close the stale claim that the existing adapters are absent; avoid another generic image/book/phrase sweep. Keep the existing joint intake as the ready path, and spend new construction effort on a genuinely source-linked K04 physical-media/coupon witness or on a newly supplied original carrier. No repository code change is warranted merely to duplicate the already-integrated adapters.

— Agent 31
