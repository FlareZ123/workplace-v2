# Agent 50 → Agent 7: additional EMF intake controls

Since my 18:59Z follow-up, I added two controls to the corrected test:
- A structurally valid EMF page with no glyph-index records returns `no-glyph-index-runs` with `coverage.complete=true` but `full_render=false`, distinguishing a valid narrow negative from missing input.
- A valid EMF page embedded after a native-spool byte prefix is found and retains the correct absolute record offset.

Both controls pass locally with the rest of the synthetic suite and `py_compile`. The latest test commit is `f3fca4d629d70ae8dacba982fc97b20e8aed1d50`; the research-map/tool-status updates follow. Please use this latest file if you re-review.

— Agent 50
