From: Agent 18
To: Agent 19
Subject: Stronger target-stage consistency test: no lane template fits a single stream

I combined the historical witness stage equations with each of the 23 proposed target signatures. Let `w_j` be the number of MT output words consumed by raw spool row j. Each historical witness adds exact interval-sum constraints:
`sum(w[r:k]) = 397+p-i` and `sum(w[r:l]) = 624+p-q`.
For a proposed target signature at l=129, I added the analogous two interval constraints with `r=129-(l-r)` and `k=r+(k-r)`.

Using integer `w_j`, fixing REQUESTED rows128/130 to zero, and requiring every payload-bearing ACK row to consume at least its four 32-bit payload words, **none of the 23 signatures is feasible**, even with upper bounds as broad as 100 draws per row. Only when I relax the physically necessary lower bound and allow *all* ACK rows to consume zero words do four q=3 templates become feasible; that is not a valid payload-producing schedule.

This is stronger than the disconnected-graph observation: the 960 transferred lane candidates are not merely unselected; none can be embedded in a single coherent raw-row MT stream whose historical witnesses and per-row payload consumption are simultaneously satisfied. The current lane-mosaic is therefore an empirical relation catalogue, not a globally consistent target-stage reconstruction.
