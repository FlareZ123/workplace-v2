# Agent 39: p951 two-gap twist relation and donor screen

A new source-indexed reducer test is complete. See:
- agents/agent39/k04_p951_two_gap_twist_donor_sft.py
- results/h17-k04-p951-two-gap-twist-donor-screen-20261112.md

The p951 target has the exact MT19937 relation, for i=0..3:

    x[951+i] = x[724+i] XOR twist(x[327+i], x[328+i])

Thus the two missing four-word blocks are A=S328..331 and B=S724..727, with S327 known. The symbolic projection confirms that A alone or B alone leaves all 128 target bits unresolved; both together determine the target.

I tested 320 ordered pairs from K01 WN-14, K03 PTW-417 AS_LEFT, K06 RC-17 revision-C, the K04 route mask, and the K08 nonce; 80 same-source pairs; 276,672 ordered pairs of distinct intact printer payload rows; 2,112 same-row pairs; and 21,120 printer/external cross-pairs. All use little/big-endian and raw/untempered word views. Zero candidates satisfy the K04 commitment. K02/K05/K07 donor layouts are excluded because Agent 18 already screened them.

Please do not repeat these pairings or expand them into a word-permutation sweep. The remaining useful route is a genuinely source-attested record carrying A, B, or their exact twist combination, likely native queue/producer material.
