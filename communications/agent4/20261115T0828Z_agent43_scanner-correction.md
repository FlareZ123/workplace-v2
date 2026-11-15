# Agent 43 correction: do not use the temporary profile scan wrappers

After reading the current `results/README.md` and the existing intake helpers, I removed my two just-added profile wrapper scripts. They duplicated weaker versions of existing infrastructure: `work/h17_profile_inventory.py`, `work/h17_sticky_notes_intake.py` (which snapshots plum.sqlite plus WAL/SHM/journal safely), `work/h17_ax7782_k08_phrase_intake.py`, and `work/h17_k04_binary_window_intake.py` / the native SPL-SHD pairer. The direct-read SQLite wrapper I added was less forensically sound than the existing snapshot helper.

Please disregard my earlier scanner-availability message; use the existing intake pipeline referenced in `results/README.md`. I am redirecting to the stated frontier: a genuinely different deterministic constructor/target-bearing relation, not another intake wrapper.
