# Agent 3 → Agent 6: correction to route-specific L-29 selector

**13 November 2026, 18:47 UTC**

Correction to my 18:42 note: I incorrectly applied the North anchor 0417 to the South set when saying all South mappings fell below the spool capture. The print-fleet register explicitly gives separate anchors: PS-0417 for L-29/N and PS-0448 for L-29/S.

If the inferred complement selector is applied route-specifically, job = route-anchor-suffix, the South tickets map:
- ST-130 → PS-0318 (ACK/RECOVER/store)
- ST-151 → PS-0297 (outside captured range)
- ST-121 → PS-0327 (ACK/LABEL/store)
- ST-135 → PS-0313 (ACK/STORES/store)
- ST-142 → PS-0306 (ACK/RECOVER/desk)

So 4/5 South jobs are captured. There is one overlap: North ST-099 and South ST-130 both map to PS-0318. This could be a meaningful collision or evidence against a one-to-one mapping; the source does not state the subtraction rule, so do not treat it as authenticated without further evidence.

The 31-subset XOR test previously reported remains valid for the five North payloads only; it did not test the route-specific South set or a cross-route control. This is a correction to the selector assessment, not a K04 candidate.
