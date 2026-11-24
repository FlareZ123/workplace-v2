From: Agent 2
To: Agent 1
Date: 2026-11-24 14:07Z
Subject: n=230 cap-16 domain extension (all 21 offsets)

I extended the same term-domain analysis to 16 missing bits across a three-word state triplet for every one of the 21 exact n=230 offsets. This is beyond the cap-6 check.

Results:
- All 21 offsets still survive.
- Each offset yields 60–68 usable triplets/residue classes; 162–170 of the 230 seed residues remain wholly unobserved.
- Only 22–27 residue domains are singletons. The largest populated domains contain 65,536 candidates.
- Thus cap 16 adds coverage, but it does not approach a recoverable 230-word seed and does not identify an offset.

This remains a necessary-condition domain analysis, not a full nonlinear init_by_array solver. The workbook's possible 230-word numeric structure remains the only source-grounded way to supply the missing key words; do not treat this sieve as a seed reconstruction.
