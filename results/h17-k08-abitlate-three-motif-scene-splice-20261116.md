# K08 A BIT LATE / A TEAL BIT anchored scene-splice trial (16 November 2026)

Agent 22. **No original K08 match in 13,982,976 complete source-motif candidate assignments.** K04/K08 remain unresolved; six other slots and the official verifier were unchanged.

## Hypothesis

The [14 November note-initialism screen](h17-k08-note-initialism-phrase-screen-20261114.md) finds the post-heading first-word initials **ATEALBIT** in N02, N06, N11, N13, N17, N18, N20, N23. A source-unverified reading is **A BIT LATE**, a plausible late-watch expression; the literal segmentation **A TEAL BIT** is an alternative. The earlier result checked initial-constrained short products and exact standalone wording, but no longer three-scene anchored composition.

Predeclare a finite authoring rule: select one source-preserved contiguous 2–6-word sea span, one late-watch span, and one crew/table span. Retain **sea → time → people** relative order from Emily's N20 and insert either full three-word anchor at one of four boundaries (before, between, after). No invented connectors or changes inside the three spans.

| Role | Specific source records | Required word in span | Distinct 2–6-word spans |
| --- | --- | --- | ---: |
| Sea | N01, N08, N14, N20, MAIL11 | sea, water, window, horizon, colors | 96 |
| Time | N02, N06, N13, N20, MAIL11 | watch, night, morning, end, lamp, quiet | 153 |
| People | N02, N09, N11, N19, N20, MAIL20 | people, table, voices, room, mugs, hands, cup, cups | 119 |

Total **96 × 153 × 119 × 2 × 4 = 13,982,976** complete candidate checks (execution count; distinct normalized strings need not be equal).

## Executed check

Original ZIP-export note SHA256: 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb. MAIL11 SHA256: f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29. MAIL20 SHA256: e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71. Original route, desk nonce, official acceptance and K08 target were unchanged.

Each complete phrase uses the original lowercase ASCII normalization, 16-byte nonce HMAC-SHA256, first-16-byte truncation, then SHA256 of those bytes against the full original K08 commitment. **N02 known authentic draft HMAC16 positive: PASS** (BF889359B0303F2B2B2FD96AE841210B). **One planted complete in-domain positive: PASS exactly once.**

The native C++17/OpenSSL local execution completed all **13,982,976 original commitment comparisons**, **zero authentic matches**. Two earlier local Python attempts each timed out at 120 seconds; they are failed executions, not negative results. A simpler portable standard-library Python reproducer is saved at [agents/agent22/k08_abitlate_scene_splice_sft.py](../agents/agent22/k08_abitlate_scene_splice_sft.py). It generates exactly the same 96/153/119 sorted source groups, all eight anchor/position combinations, and includes both whole-phrase controls. The tested newline-joined sorted span hashes were: sea bbcfb9b66e13f686046522467706daf3cda706afe1e00ad1aab0ace16dec0771; time 9c3161fbaf2e9b1950c0ac2a13f5ad7e41d6763b6f59bdbdc1eced0c7a5f6380; people b87ae17b0f65e611475d2b87f8d0e37743b033a5835d119ef8ef6561530de0f7.

## Decision

The specified three-scene composition with either exact anchor does not yield K08. This narrow negative says nothing about a different final sentence, image representation or non-literal editing rule. It recovers no K04 bits and no historically authenticated K08 words. Avoid merely enlarging the anchor/connector grid without a new source cue.
