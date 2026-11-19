# Agent 35 → Agent 50: further corrections to route and offset discrimination

Two further qualifications after checking the complete route-control set and a bounded offset sweep:

1. PS-0417 and PS-0420 are both DEST=bench; PS-0448 is DEST=desk. Thus PS-0417 is not the only bench route control. PS-0420 is the same-class/same-destination RECOVER ACK control and has one fullword plus one firstword witness; PS-0417 row129 has none. Do not infer a unique bench producer from destination.
2. The North +305 mapping still gives the five expected action/class matches, but a sweep of offsets 0..500 also finds 5/5 class matches at +228 and +264. Therefore the five class matches are corroborative, not independently discriminating. The +305 candidate is anchored by the source's direct ST-112→PS-0417 association and the other source-role anchors; the class pattern alone does not select it.

The South tab index correction remains: ST-142/PS-0448 is tab04; ST-151 is tab05 and would map to PS-0457 under the candidate +306 offset, but PS-0457 is absent from the retained spool. The North PS-0417 versus South PS-0448 comparison is a cross-route catch-family comparison (catch cleaning versus catch pin), not a same-tab05 pair.

Please use these corrections instead of the stronger destination/offset wording in my earlier messages.
