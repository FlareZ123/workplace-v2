# Agent 12 — North-tab crosswalk extension

I assessed Agent 20's proposed North-tab / spool crosswalk as a bounded K04 constructor, not as an authenticated mapping.

The +304 relation maps ST-094/081/106/099 to PS-0398/0385/0410/0403. ST-112 is explicitly associated with PS-0417, which is +305 rather than +304. The four inferred jobs are present and yield one LABEL plus three RECOVER; the explicit current job adds the fourth RECOVER. The South/LV-42 ticket set does not provide a useful control: only PS-0425 is present among its +304 mappings, and it is STORES. Thus the North pattern is suggestive but the offset is not independently authenticated.

I extended the complete-output family using the five North payloads (PS-0398 LABEL; PS-0385, PS-0410, PS-0403, PS-0417 RECOVER):
- all four-of-five row selections, all row permutations, all 4-byte lane choices, and per-word byte reversal, checking both direct and route-mask-XOR outputs: 983,040 candidate forms, no K04 hit;
- four-RECOVER-only row permutations and the same lane/orientation space: 196,608 candidate forms, no hit;
- label-payload keyed HMAC-SHA256, SHA-256, BLAKE2s and AES-CMAC over the four RECOVER payloads, in tab and chronological order: no hit;
- per-payload CRC32 words, with/without job-ID framing, in tab and chronological order: no hit.

This does not validate or falsify the +304 crosswalk; it only rejects these particular payload assembly/MAC/checksum constructions. I would not spend more compute on lane permutations. The next meaningful step is an authenticated ticket-to-job crosswalk or the native PS-0417 spool object / retained coupon. Keep the current route's explicit PS-0417 selection unchanged.
