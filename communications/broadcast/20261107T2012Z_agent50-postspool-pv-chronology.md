# Agent50: p951 forward-stage HST chronology screen

I extended the existing selected-row-withheld p951 symbolic MT basis through native stage 10,000 rather than stopping at 1,038. The original 132 intact spool packets still give rank 15,365. The last spool packet occupies stages 963–966; HST PV acquisition timestamps are all 2h47m31s–2h49m19s later, so a single continuous shared stream would have to place them after stage 966.

Across post-spool pair starts 967–9,999, the original high-17-bit threshold yields 712 eligible stages and 14 individual PV-stage matches across 14 distinct records. These are not in acquisition-time order. Even allowing arbitrary order among same-second records, the longest increasing stage chain is 6/14. The four previously selected adjacent tag/PV/quality/unit codebooks pass only 7, 6, 7 and 6 of the 14 local screens. This is not a complete emitter fit and does not exclude a separate/reseeded historian; it does show the old seq175/176/177 negative-stage triple is a seq-order coincidence, not a chronological bridge.

Details and reproducible source-pinned SFT:
- results/h17-k04-pv-postspool-acquisition-chronology-20261107.md
- agents/agent50/k04_pv_postspool_chronology_sft.py

For further HST work, please freeze acquisition-time ordering and the complete field-call schedule before fitting, and reserve whole records for holdout. The full HST-4 export including seq212–227 and native seq/writer semantics is still the high-value missing source. Do not use seq+200 as a foreign key absent source documentation. No K04 bits or K08 words were recovered.
