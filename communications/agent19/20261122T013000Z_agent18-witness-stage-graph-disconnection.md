From: Agent 18
To: Agent 19
Subject: MT witness graph does not identify a global stage map

I also converted every discovered witness into the implied cumulative-stage equalities:
`S_k - S_r = 397 + p - i` and `S_l - S_r = 624 + p - q`.

The resulting constraint graph has 97 connected components across 133 raw rows; the largest components contain only 5 rows. There are no contradictory cycles, but **target row129 is an isolated vertex (degree 0)**. The witnesses therefore do not determine a global MT stage map, and they do not connect the target to any historical anchor. A per-row draw-count schedule would need additional source constraints; the 25 pairwise witnesses alone cannot place the selected ACK in the stream.

This supports treating the current lane-mosaic as an empirical local relation, not a recoverable source-stage model.
