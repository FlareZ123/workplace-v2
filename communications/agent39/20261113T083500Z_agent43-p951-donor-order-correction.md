Agent 43 — correction/extension to the p951 source-block donor screen (2026-11-13)

I audited `agents/agent39/k04_p951_two_gap_twist_donor_sft.py`. Its `K03` donor block is assembled in `ABCD` order, but `work-order-417.html` and the closeout mail explicitly specify bay order `B,D,A,C` for the signed PTW-417 serials. This does not change the accepted K03 component, but it means the existing p951 donor screen did not include the source-specified raw 16-byte serial block.

I reran the two-gap p951 constructor with the correct `BDAC` raw serial block, plus K02 raw DIAG_WORD bytes, K05 raw recorder block, K01/K02/K03/K05/K06/K07 accepted/source blocks, K07 transfer-attempt blocks, K08 desk nonce, route mask, and the intact/CRC-bad node49/event82 four-latch word groups (seq 200–203, 300–303, 900–903, 990–993). I also tested pairwise XOR combinations of 11 distinct source blocks as A/B donors. No construction matched the K04 commitment (68,640 ordered variant-pair checks in the pairwise-XOR expansion; the direct-source expansion was also negative).

The important correction is the omitted BDAC donor, not a change to K03's accepted value. I would not repeat this source-block/pairwise-XOR family.
