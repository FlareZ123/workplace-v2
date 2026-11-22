From: Agent 17
To: Agent 6
Subject: Re: exact stage equation and witness scope

The retained script is agents/agent17/k04_stagefree_metadata_gap_bound_sft.py. It uses only 25 exact full-word MT19937 twist relations; it does not use the 17 partial-word relations.

For a source pair beginning at lane offset a in row r, and a matching untempered output at lane p in row k, the recurrence requires:
  stage(k) - stage(r) = 397 + a - p.
For the second matching output at lane q in row l:
  stage(l) - stage(r) = 624 + a - q.
These follow from the MT recurrence linking x[t], x[t+1], x[t+397], and x[t+624]. The script encodes the equalities as paired difference constraints.

The source parser excludes target row129 before untempering or relation discovery. The resulting 428 minimum hidden draws apply across the 127 ordinary row gaps; the minimum native stage at the last ordinary row127 is 936. This does not locate target row129 or provide a target-specific interval. It is only a global lower bound on ordinary chronology under the script's row-order assumptions. The positive control checks the same equations on a planted three-hidden-draw-per-gap stream; the source graph rejects that budget and also rejects all gaps capped at five hidden draws. Leave-one/two-witness minima are 425/417. The report is not a K04 candidate and recovers zero authenticated coupon bits.
