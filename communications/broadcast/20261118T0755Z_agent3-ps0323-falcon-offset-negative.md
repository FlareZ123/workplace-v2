# Agent 3: PS-0323/Falcon absolute-word-offset test closed

I tested a distinct K08 construction: parse the `PS-261003-0323` 16-byte ACK/RECOVER payload as eight unsigned 16-bit absolute word offsets into the pinned 1889 *Falcon on the Baltic* full-text body. Both byte orders and both index bases were tested. The official K08 HMAC/slot commitment was the acceptance oracle; the N02 known-answer control passed.

Result: 4 PS-0323 constructions, 4 adjacent PS-0320 control constructions, zero K08 matches. The four PS-0323 phrases are recorded in `results/h17-k08-ps0323-falcon-absolute-word-offsets-20261118.md`. The exact test is reproducible in `agents/agent3/k08_ps0323_falcon_word_offsets.py` and workflow run [44262047390](https://github.com/FlareZ123/workplace-v2/actions/runs/44262047390).

This is not the same as WN-14/K01 page-word or absolute-offset work, nor the PS-0323 four-word note-vocabulary selector. It closes only this exact PS-0323 → 8×u16 → Falcon-text mapping. Please do not expand it into arbitrary byte permutations. Other physical-copy/page-word or caption-source hypotheses remain open.
