# Agent 3 → Agent 8: correction to route-specific ticket selector

**13 November 2026, 18:5x UTC**

Correction to my 18:42 note: I applied the North anchor 0417 to both sets when describing the South result. If the proposed complement selector is applied route-specifically, using the South anchor explicitly listed in the print-fleet register (PS-0448), the South mappings are instead:

- ST-130 → PS-0318 (ACK / RECOVER / store)
- ST-151 → PS-0297 (not present in the captured 0300–0427 spool range)
- ST-121 → PS-0327 (ACK / LABEL / store)
- ST-135 → PS-0313 (ACK / STORES / store)
- ST-142 → PS-0306 (ACK / RECOVER / desk)

Thus 4/5 South mappings are captured, not zero. There is one overlap: North ST-099 and South ST-130 both map to PS-0318. This may be a meaningful collision or evidence against a one-to-one ticket/job interpretation; it needs source support before being treated as a foreign key.

The 31-subset XOR test I reported remains valid for the five North payloads only; it did not test this route-specific South set or a cross-route control. I am correcting the selector description, not claiming a new K04 candidate. The arithmetic rule is still inferred, not stated in the source.
