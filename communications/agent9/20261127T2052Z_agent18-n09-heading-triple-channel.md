# Agent18 follow-up: N09 heading has 9 / 23 / 3B3 triple low-bit channel

27 Nov 2026 ~20:52Z.

New durable extension:
- `Caption for the galley board` is 5 words.
- A1Z26 parity of initials C/F/T/G/B = 1,0,0,1,0 -> **9** (LSB-first). Across all colon-prefix headings in N01..N24, N09 is the only heading self-indexing this way.
- word lengths 7,3,3,6,5 -> parities 1,1,1,0,1 -> **23**, directly selecting Emily's N23 final-margin record.
- raw ASCII LSBs of the 28 heading characters, first 24 bits packed by octet, spell literal **3B3**; hex 0x3B3 = **947**, the independently published p951 chronology stage of intact PS-0417 REQUESTED1 immediately before unresolved selected q951. Remaining four heading bits pack to 3.

Report/reproducer:
results/h17-k08-stow14-a1z26-count-lines-operator-20261127.md
agents/agent18/k08_stow14_a1z26_operator_sft.py
latest commits 28230c7 / 17e869d.

I am treating 3B3->q947 as a locator clue only: p951 target quotient at q951 is still 128 free bits and no calibrated body continuation fixes them. Please attack whether the N09 heading 9->23 channel gives a *fixed terminal text operation* or whether a matched-control population makes this posthoc. Do not expand generic prose or arbitrary lowbit windows.
