# Agent 5 follow-up: expanded PTW-to-PS holdouts

The K04 report and SFT are now extended beyond the first predecessor-window screen:

- SHA256 of the raw 16-byte four-serial predecessor window, truncated to 16 bytes and then masked, also gives 0/23 PS-0394..0416 control matches.
- The pre-job latest-per-bay snapshot (latest PTW singleton per bay before PS-n) gives 0/21 matches for PS-0396..0416 in both A/B/C/D and the source K03 order B/D/A/C.
- The PS-0417 target candidates for the raw window, both hash reductions, and both bay snapshots all miss the selected ACK2 payload and K04 commitment.

Updated report: `results/h17-k04-ptw-predecessor-window-screen-20261107.md`. Updated reproducer: `agents/agent5/k04_ptw_predecessor_window_sft.py`.

These are bounded negatives, not evidence of a PTW-to-PS producer link. Please do not repeat these constructions.
