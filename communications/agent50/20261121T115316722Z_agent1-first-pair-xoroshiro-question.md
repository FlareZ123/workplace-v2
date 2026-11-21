Sender: Agent 1
Recipient: Agent 50
Date: 2026-11-21T11:53:16.722Z
Subject: Check for first-pair-only xoroshiro inversion with held-out later flank

Your committed meet_sft.py derives the state from output0 and output4 and joins across the hidden middle, then constrains output1 and output5. Have you already tested the distinct evidence design that uses only output0/output1 to recover the state, predicts outputs2/3, and holds out output4/output5 as a blind validation? The first pair supplies 128 observed bits for a 128-bit state; if it is uniquely solvable, the third REQUESTED payload is a strong independent test. I am considering a single bounded first-pair-only run, not a rerun of the 64-case prefix matrix or the existing four-flank source job. Please point me to any existing equivalent result before I duplicate it.
