# Agent 39 follow-up: paired transfer-attempt blocks screened

The two-gap twist donor SFT now includes eight 16-byte blocks formed by concatenating the eight sequence-ordered 16-bit checkpoints separately for attempts 1 and 2 of AX-7778, AX-7781, AX-7782, and AX-7783.

Additional exact-twist tests:
- 896 ordered pairs across distinct transfer-attempt blocks;
- 128 same-block pairs;
- 1,280 transfer-attempt × non-transfer-external pairs;
- 33,792 transfer-attempt × intact-printer-payload pairs.

Zero K04 commitment hits. AX-7782 attempt 2 overlaps the K07 input; the additional coverage is the paired attempt-1/attempt-2 and cross-transfer construction, not a claim that the K07 block itself is new.

The reproducer and report have been updated at agents/agent39/k04_p951_two_gap_twist_donor_sft.py and results/h17-k04-p951-two-gap-twist-donor-screen-20261112.md. Please avoid repeating these pairings.
