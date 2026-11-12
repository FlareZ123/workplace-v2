# Agent 6 follow-up: node49 immediate seq/latch sampler controls

Additional narrow check for the event/latch/seq part of your question, using the same five p951-matched node49 controls and no target/commitment data. For each control at p=-322,-321,-316,-315,-313, I decoded the adjacent source-fixed top bits as CPython randrange outputs.

At p+1, the 10-bit randrange(1000) values for seq990, seq201, seq992 and seq203 are respectively 49, 521, 448 and 529; all are <1000 (so no rejection), and none equals its original sequence field. The seq993 record's p+1 top10 bits are not source-fixed. At p+1, the 3-bit randrange(4) values for latches 0,1,2,3 are 0,4,3,4 respectively; 4 is rejected by randrange(4), while the two accepted values 0 and 3 match only one of the four original latch values (seq990=0; seq992=2 is not 3). The remaining two would require a later draw after rejection, whose full 3 bits are not fixed for those records.

Thus the simple immediate one-draw-per-field mapping is also not supported. This does not test a different call order with rejection or a different source position, and I will not broaden it without a source-defined schedule. No selected K04 bits gained.

— Agent 6
