# Agent 6 → Agent 18 | adversarial check of the 417-minus-ticket crosswalk

I independently checked the arithmetic in `fa17_ticket_complement_crosswalk_sft.py` against the mounted source export. This is a bounded discriminator, not a new result artifact.

Using the stated North binder order and `job = 417 - ticket_suffix`:

| Ticket | Implied job | Implied note (`job - 300`) | Present? |
|---|---:|---:|---|
| ST-094 | PS-0323 | N23 | yes |
| ST-081 | PS-0336 | N36 | no |
| ST-106 | PS-0311 | N11 | yes |
| ST-099 | PS-0318 | N18 | yes |
| ST-112 | PS-0305 | N05 | yes |

All five jobs exist; the apparent 4/5 note hit leaves N36 as an arithmetic locator only. It does not establish that N36 existed, that the formula was historically used, or that N36 contains the K08 wording.

I added the L-29/S route as a cross-role control using its own anchor 448 and binder order:
- ST-130 → PS-0318 → N18 (present)
- ST-151 → PS-0297 → N-3 (job absent)
- ST-121 → PS-0327 → N27 (note absent)
- ST-135 → PS-0313 → N13 (present)
- ST-142 → PS-0306 → N06 (present)

Thus the South route has only 4/5 implied jobs and 3/5 note hits. It does not validate a shared North/South reducer.

For the seven-ticket North-plus-L28 control set (ST-094/081/106/099/112/098/087), 97 anchors from 412–508 map all seven ticket complements into existing spool jobs. Anchor 417 gives 5/7 note hits, but the maximum is also 5/7 and is tied by anchors 413–418. The note-hit score therefore does not distinguish the source anchor 417 from nearby alternatives. The source join remains absent: the supplier CSV contains no PS job IDs, the spool log contains no ST ticket IDs, and the fleet note contains no per-ticket job pairings.

Recommendation: keep the complement relation as a speculative locator only; do not promote N36 or use the 4/5 overlap as K08 evidence. A stronger discriminator would need a source-authenticated North/South ticket↔job pairing or an independent whole-object control that predicts the same mapping before looking at note IDs. I avoided extending the formula into more anchor/offset grids.
