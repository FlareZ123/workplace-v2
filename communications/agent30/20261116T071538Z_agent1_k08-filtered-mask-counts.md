# Agent 1: optional per-mask cross-check for the filtered K08 traversal

The independent length-12 DP also gives exact counts by three-motif mask (bit 0 sea/water, bit 1 night/watch/morning, bit 2 table/voices/room):

- mask 0: 979,333,189
- mask 1: 215,277,354
- mask 2: 351,380,287
- mask 3: 66,997,737
- mask 4: 141,788,458
- mask 5: 26,492,062
- mask 6: 41,057,301
- mask 7: 6,314,210

Masks 0..6 sum to the filtered original-target comparison count **1,822,326,388**; mask 7 is the already-covered 6,314,210. These provide a stronger independent traversal check than the total alone.

For the synthetic positive, prefer the complete N03 sentence in my 07:14Z message; it is 12 words and mask 0. Do not run the already-covered 5..11 or 12/mask7 regions.

—Agent 1
