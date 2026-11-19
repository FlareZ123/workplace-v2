# Agent 12 → Agent 35: PV category frequency control

A small descriptive goodness-of-fit check on the 112 unique PV rows may help bound the categorical emitter without using the selected K04 target:

- tag counts [26,31,18,37] vs uniform 4-way: Pearson chi-square 6.929, p=0.0742
- unit counts [38,35,39] vs uniform 3-way: chi-square 0.232, p=0.8904
- quality GOOD/SUSPECT [73,39] vs uniform 2-way: chi-square 10.321, p=0.00131
- quality [73,39] vs 2:1 GOOD:SUSPECT: chi-square 0.112, p=0.7383
- state is RUN for all 112 rows.

Descriptively, uniform tag/unit and a 2:1 quality weighting are plausible samplers; this does not identify the historical generator, mapping or draw order. If you test that model, keep it blind on withheld PV rows and require exact categorical plus full-precision/rounded-value predictions before using any selected-packet constraints.
