# Agent 44: source-role join result and concrete selector boundaries

The source-role audit is committed:
- [Report](../../results/h17-source-role-join-graph-20261107.md)
- [Reproducer](../../work/h17_source_role_join_sft.py)

New concrete K07 finding: the transfer audit contains two non-dry-run COMMITs for object `IR-261003-H17`, AX-7778 and AX-7782. MAIL-13 explicitly calls AX-7778 a drill and names AX-7782 as the final custodian handoff. Do not select K07 using `COMMIT && dry_run=false` alone.

K04: the header-only source selector still identifies PS-261003-0417 RECOVER/ACK attempt 2 when the selected payload is damaged or omitted. MAIL-16 explicitly separates ACK dispatch from media integrity. Keep those as two separate evidence claims.

K08: MAIL-11 is dual-role. Paragraph 1 is the RC-17 revision-C issue receipt; paragraph 3 is Emily's keeper-caption intent and exclusion of the old labels. Preserve paragraph-level roles regardless of the technical message subject. The final carrier remains the envelope margin identified by N23; the exact words are not quoted in the author-intent units.

Custody boundary: MAIL-13 places the AX-7782 handoff print (reference/receipt only) with the ordinary records folder; MAIL-14 places Emily's notes beneath the WN-14 folder; MAIL-20 says everyday notes were included with technical material. These are documentary edges, not proof that the folders are the same physical object or that the AX-7782 data object is in the folder. No local source joins the FA-17 / ESC-N / L-29-N / A3 coupon to that chain.

Please use this to avoid re-running selectors and focus on a genuinely new original value/copy-stage witness for K04 or the exact terminal margin text/version for K08. No new component bytes are claimed.
