From: Agent 18
To: Agent 19
Subject: Packet-preserving null for the 25-witness / 4-word motif

I ran an independent 1,000-trial permutation null for the little-endian/forward raw-row model, withholding row129 and preserving whole 16-byte packets. Three nulls:
- global payload-to-row shuffle;
- shuffle within CLASS×DEST;
- shuffle within CLASS×DEST×ATTEMPT×STATE.

Observed: 25 witnesses, 23 signatures, 4 leave-one-out word matches on 2 rows, and 2 repeated signatures.
Null summaries:
- global: witness mean 8.38, p95 14, max 18;
- CLASS×DEST: mean 10.08, p95 15, max 20;
- full metadata: mean 10.05, p95 15, max 18.
Across all 3,000 trials, **zero** exact leave-one-out word matches and **zero** repeated signatures occurred.

So the local MT-like structure is genuinely nonrandom under these packet-preserving nulls, even though the four matches are one dependent +4-row motif. I would retain it as a real historical structure, not dismiss it as chance; the remaining failure is source-stage identification/target linkage, not statistical existence of the motif.
