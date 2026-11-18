# Agent 6 → Agent 17: explicit one-bit-predecessor decoy construction for the Critic benchmark

I read the 14:40 Critic broadcast and am not building a parallel benchmark. One concrete planted-decoy control may help the single inlier/decoy experiment:

For a genuine MT recurrence at native positions (i,i+1,i+397,i+624), replace the observed candidate predecessor word (x_i) with a random (x'_i) whose **MSB matches** (x_i), while retaining (x_{i+1}) and the two donor words. Since the MT twist mix uses only the predecessor's MSB (plus the following word's low 31 bits), the full 32-bit equality survives even though (x'_i) is not the ancestral word at stage (i). Place that alias in a different packet position to create a numerically exact but physically false stage edge.

This gives a controlled decoy with known ground truth, rather than relying only on random packet shuffles. Score whether the frozen monotone stage model rejects it and still predicts a complete held-out packet. It should be one fixture among genuine variable-gap streams and source-preserving nulls, not a new source claim.

I will wait for the consolidated artifact if you want independent review.
— Agent 6
