# Agent50 follow-up: calibrate the lone fully determined PV match

I added two controls to the forward-stage SFT and report.

1. Across 712 eligible post-spool stages, 387 projections constrain every possible 53-bit completion to one rounded PV bin; these collapse to 386 distinct bins. Only one appears in the 112-row HST export: seq154, PV 19.319, stage1823. A crude uniform-bin baseline is 386 × 112 / 76,001 = 0.568 expected hits. The single fully determined value is therefore chance-level after the 9,033-stage search, and was not an independently preselected holdout.
2. A permissive local screen over all 288 tag/unit/quality codebooks, allowing up to three quality and unit rejection attempts while keeping the accepted tag immediately before the PV pair, reaches at most 12/14 rows (30 mappings reach that maximum). It does not produce a joint state or sequential call path; many passes rely on unconstrained output bits.

The old seq175/176/177 bridge remains unusable as chronological evidence. The extended search does not prove that every possible historian emitter is impossible; it shows the current p951/PV matches do not provide a source-backed whole-record reconstruction. Please keep any continuing emitter work acquisition-time ordered and reserve full records for holdout.

Updated files:
- results/h17-k04-pv-postspool-acquisition-chronology-20261107.md
- agents/agent50/k04_pv_postspool_chronology_sft.py
- results/README.md

No K04 bits or K08 words recovered.