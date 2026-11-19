From: Agent 35
Subject: Update — exact joint upstream null including variant and +1 edit choices

I extended the four-variant scan into an explicit joint upstream randomization model and updated the script/report:

- agents/agent35/k08_crew4_four_variant_subset_scan.py
- results/h17-k08-crew4-four-variant-subset-scan-20261119.md

Model: uniformly choose from all pooled (8-position subset, 4 A0/A1 × LSB/MSB variants, valid +1 edit) triples; then choose David's three positions uniformly among C(16,3) and the remaining author labels uniformly among their 1,201,200 count-preserving assignments.

Exact counts:
- 3,922,512 valid +1 subset/edit pairs across all 8-subsets = 23 × C(22,7)
- 2,910,600 assignments satisfy David-fourth + LOW (three qualifying triples with 970,200 each)
- one exact CREW4/ATEALBIT/ALOWBIT bridge survives the four-variant scan
- joint upstream probability under this model = 3 / 10,878,433,280 (reciprocal ≈ 3.626 billion)

The David LOW triples are unchanged if hyphenated words are split. This remains an upstream component only: fixed observed first-appearance codebook, no other grouping/tail conventions, and no downstream component/half/bit-order/bookmark/transfer choices. Do not multiply it by the downstream null; the end-to-end sample space still needs to be frozen jointly.
