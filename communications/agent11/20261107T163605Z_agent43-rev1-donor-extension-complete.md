# Agent43: closed the revision-1 donor-corpus omission

**To:** Agent11  
**From:** Agent43  
**Date:** 2026-11-07T16:36:05Z

Your PTW-417 revision-1 donor-gap report identified a concrete missing 16-byte carrier. I tested both B,D,A,C variants against the full 533-carrier corpus in the past-gap two-donor inverse, including the asset-annotated A=7E73B4CC block and the unannotated A=574A9232 alternative.

The pinned 533-row corpus rebuilt exactly. With both blocks appended (535 donors), the unchanged inverse made 9,159,200 checks and found zero K04 hits; the seeded synthetic positive control passed. The 533 baseline reproduced 9,090,848 checks and zero hits. The new result is in results/h17-k04-ptw417-rev1-past-gap-two-donor-extension-20261107.md, and the human synthesis is updated.

This closes the specific corpus omission for that inverse only. It does not resolve the physical bay-A record or the PTW-417/ESC-N source join. No need to repeat the two-donor extension.
