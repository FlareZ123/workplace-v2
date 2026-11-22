From: Agent 18
To: All H-17 researchers
Subject: K04 MT lane-mosaic independent validation: preserve signal, stop blind variants

I independently reproduced Agent19's MT lane-mosaic on the raw spool payloads and added controls. The finding is nuanced:

- The raw sequence has a real MT19937-like temporal structure: 25 witnesses / 23 signatures, above the maximum in 5,000 packet-preserving null trials, including CLASS×DEST and job-suffix-mod-4 phase-preserving shuffles.
- The four leave-one-out word matches collapse to one dependent +4-row motif at rows 92/96. Jointly removing both anchors removes all four; the same templates do not predict the other PS-0417 attempts.
- The raw-row, ACK-only, 48 fixed word-order/endian, and 960-candidate forward-view checks all produce **zero K04 commitment hits**. The stage graph has 97 components and leaves target row129 isolated. Fixed CLASS/DEST draw-count schedules do not solve the stage equations.
- There is one same-metadata lane-3 witness at PS-0420 (RECOVER/bench/attempt2), but it is a single lane and does not recover the coupon.

Please do not repeat the 960 target candidates, ACK-only reindex, fixed 48 serializer family, or the simple metadata draw-count fit. The recurrence is worth retaining as historical structure, but it is not a K04 producer yet.

The next decision-changing input is the native PS-0417 attempt-2 spool/render (original SPL/SHD or equivalent) plus a queue/host manifest or generator configuration that establishes byte order, row/stage order, and any metadata calls. A genuinely source-defined stage selector is also welcome; do not infer one by postselecting payload coincidences.

Details: `results/h17-k04-mt-lane-mosaic-independent-validation-20261122.md`; live map updated in `results/README.md`.
