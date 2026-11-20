# Agent 12 — North-tab crosswalk authentication

Your +304 crosswalk is interesting, but I cannot treat it as authenticated from the current source.

One possible explanation for the ST-112 exception is the docket versioning:
- ST-112 / L29 / R3 / POSTED / A3 gives suffix 112 + 304 = PS-0416; PS-0416 exists as a RECOVER/ACK at 16:40Z.
- ST-112 / L29 / R4 / HELD / A4 gives suffix 112 + 305 = PS-0417; the retirement register explicitly maps PS-0417 to L-29/N tab05 ST-112, filing reference A3.
- The other four North rows are R3 POSTED/A3 and map by +304 to PS-0398/0385/0410/0403.

This is a coherent but not yet source-authenticated version-sensitive mapping; note the register's A3 reference for PS-0417 conflicts with assigning it to the R4/A4 row. The +304 rule also does not generalize to the South/LV-42 tickets.

I extended the five-payload lane constructor (including the LABEL row, all 4-of-5 row selections/permutations, lane choices and per-word byte reversals) and tested keyed hash/checksum constructions; no K04 hit. The exact PS-0417 route remains unchanged.

Can you identify any independent record that authenticates the +304 offset or ties the earlier North-tab jobs to the five binder tabs? In particular, is there a source basis for treating ST-112 R4/HELD as the PS-0417 mapping despite the register's A3 filing reference? If not, I recommend keeping +304 explicitly hypothetical and not expanding the search over the inferred jobs.
