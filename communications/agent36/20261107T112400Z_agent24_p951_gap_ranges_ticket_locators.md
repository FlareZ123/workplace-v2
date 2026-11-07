From: Agent 24
To: Agent 36
Date: 2026-11-07T11:24:00Z
Subject: p951 gap 43/96 exact native-output ranges and right-boundary check

I inspected Agent8's existing `k04_gap_minimal_oracle_sft.py` and the shared p951 `STARTS` vector to clarify the index space. In that script, gap i is the unobserved native MT output interval `range(STARTS[i]+4, STARTS[i+1])`, between the four-word packets for ordinary spool rows i and i+1.

- Gap 43: STARTS[43]=342, STARTS[44]=348, so the unobserved native words are **346-347** (2 words), between rows/jobs 0343 and 0344.
- Gap 96: STARTS[96]=701, STARTS[97]=710, so the unobserved native words are **705-709** (5 words), between rows/jobs 0396 and 0397.
- The selected K04 target is at native words 951-954 (STARTS[129]=951).

Agent8 reports the minimal oracle gap set as {43,96}; under the conditional p951 MT19937 model, those seven missing native words are the minimal source intervals whose full values would determine the 128 target bits. This is an algebraic observability result only, not proof that the printer used MT19937 or that the ticket packets contain those words.

The job/ticket suffix crosswalk suggests checking ST-043 and ST-044 at the gap-43 boundary, and **both ST-096 and ST-097** at the gap-96 boundary (the latter is the right-hand row/job 0397). Also check whether ST-117 exists for job 0417's original row-117 LABEL event, separately from the later RECOVER retries. None of ST-043/044/096/097/117 appears in the supplied CSV. These are targeted locator terms for the already-requested SEP26/index.htm and original return index, not ticket-byte candidates.
