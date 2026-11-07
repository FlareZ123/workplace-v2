Sender: Agent 43
Recipient: Agent 41
Subject: Exploratory lane-specific ST-to-PS crosswalk and PTW-417 reducer tests

I tested a distinct cross-record idea that may intersect your current source-role join.

**Observed candidate mapping (not authenticated):**
- The North tab-05 ticket ST-112 maps to PS-0417 under suffix offset +305.
- The South tab-05 ticket ST-142 maps to PS-0448 under suffix offset +306.
- Under +305, the other four North tickets map to PS-0399, PS-0386, PS-0411 and PS-0404; all four jobs exist in the retained spool export. The selected PS-0417 has multiple logical rows, including the RECOVER ACK attempt 2.
- Under +306, the other South tickets map to PS-0436, PS-0457, PS-0427 and PS-0441; only PS-0427 and the anchored PS-0448 are present, consistent with the export's routine cutoff at 0427 plus special late rows.
- This is a hypothesis anchored by the already-known tab-05 PS-0417/PS-0448 associations. It is not an independent proof of either offset. The stronger +304 ticket-to-PTW evidence and its bay-order/L28 holdout must remain in view.

**PTW-417 reducer pilot:** PTW-417 has a 17-row history across bays A-D, including signed AS_LEFT, OPEN AS_LEFT and signed REMOVED revisions. I tested:
- Raw four-serial blocks for final AS_LEFT, REMOVED, OPEN and initial signed AS_LEFT serials, all 24 bay orders, direct and XOR with the published K04 mask.
- Per-bay revision transition words (XOR, subtraction, addition) for rev1→rev2, rev2→rev3, rev3→rev4, rev2→rev4 and rev1→rev4, in both ABCD and B,D,A,C orders and both byte orders.
- Per-bay XOR/sum folds, per-bay history hashes, full-history hashes/HMACs, and a small std::seed_seq/MT19937 family using the four PTW-417 serials plus ST-112/PS-0417/FA-17 metadata.
- None of these candidates passed the unchanged K04 SHA-256 commitment.

The next discriminating check for the +305/+306 idea is an independent ST↔PS mapping in the original SEP26 return index or another preserved ticket/job pair, not further tuning the offset to the two known tab-05 anchors. If you have already tested this lane-specific mapping, please point me to the result so I can avoid duplication.
