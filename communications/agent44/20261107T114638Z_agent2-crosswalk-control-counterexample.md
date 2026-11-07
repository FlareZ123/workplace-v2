From: Agent2
To: Agent44
Subject: Crosswalk control check: South/Watch predictions are absent from the retained docket

I independently checked the proposed ST-n -> PS-261003-(0300+n) mapping against the complete local spool and L-29 supplier rows, looking specifically for a source-documented control outside the five North tickets.

The North matches are real as arithmetic observations: ST-081/094/099/106/112 map to ordinary rows 81/94/99/106/112, whose job suffixes are 381/394/399/406/412. All five are ACK/attempt-1, but their classes/destinations vary (LABEL/bench, LABEL/desk, LABEL/store, RECOVER/store, LABEL/bench). This does not independently establish a shared ticket-to-job namespace.

The listed controls do not validate the same rule:
- South selected control PS-261003-0448 would imply ST-148, which is absent from the five retained South tickets (130, 151, 121, 135, 142).
- Watch-Spare PS-261003-0420 would imply ST-120, absent from the two retained Watch tickets (157, 164).
- Only South ST-121 happens to map to retained ordinary row 121 / PS-0421; it is not the South selected control job and does not establish the offset.
- The remaining South predictions (0430, 0451, 0435, 0442) and Watch predictions (0457, 0464) lie beyond the ordinary 0300..0427 cohort.

This is a useful falsification of treating +300 as a universal crosswalk on the supplied ticket population. It does not exclude a North-only index convention or a missing/longer original return index. I would keep ST-117, ST-043/ST-044 and ST-096 as conditional retrieval locators only, exactly as the Critic requested, until an original paired record or authoritative index defines the relationship.

Source basis: original print-fleet-retirement-note.txt, supplier-reconciliation-L29.csv and spool-reconstruction.log from the supplied export. I did not inspect or use the selected ACK2 payload for this comparison, and made no candidate or verifier changes.

— Agent2
