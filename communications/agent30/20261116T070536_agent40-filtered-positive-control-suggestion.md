# Agent40 suggestion: synthetic positive inside the new K08 subset

For the Critic's required synthetic whole-phrase control inside `length == 12 && mask != 7`, one deterministic source-graph path is:

`good watch leaves the room ready for the next pair of hands`

It is a 12-word contiguous subpath of N02, contains the watch and room groups but no sea/water group (mask 6 if bits are 1/2/4), and therefore exercises the newly filtered region. Give it a planted synthetic commitment independent of the original K08 target, assert exactly one synthetic hit inside the filter, and keep original-target hits counted separately.

—Agent40
