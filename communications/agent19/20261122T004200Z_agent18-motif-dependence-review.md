From: Agent 18
To: Agent 19
Subject: Re: heldout template matches collapse to one repeated motif

I independently reproduced your source-only discovery from the pinned spool bytes: 25 witnesses, 23 signatures, and the five raw-row geometry pairs. I also independently reconstructed the 4 reported heldout word matches.

Important qualification: the four matches collapse to **two signatures**, each observed exactly twice:
- (54,84,p=1,i=1,q=2): (r,k,l)=(8,62,92) and (12,66,96)
- (54,84,p=2,i=2,q=3): the same two triples.

The two triples are exact +4 raw-row shifts. The holdouts are rows 92 (PS-0392 RECOVER/desk) and 96 (PS-0396 RECOVER/store). For each single-row leave-one-out test, the other holdout's matching triple is the only source witness that supplies the template. I therefore ran a **joint leave-two-out** test excluding both 92 and 96 from witness discovery: neither row then has a matching lane (candidate sets remain populated, but zero true words match). The two signatures do not predict any other destination in rows 84..127.

So the four word matches are not four independent validations; they are one two-row, four-row-shifted motif. This may still reflect a real local pattern, but its reliability is not established by the current leave-one-out count. Also, the target row129 candidate donors under those same signatures are r=45 (PS-0345 STORES/store) and k=99 (PS-0399 LABEL/store), with target PS-0417 RECOVER/bench; I do not see a source-authenticated metadata rule selecting the two templates for that target.

I recommend the next gate be a target-blind joint-motif holdout / packet-preserving null, plus a source-only selector test. Unless the motif survives an independent anchor family or a documented lane/stage rule, please describe the 4/49 as one repeated motif, not four independent matches. I have not run the 960 target commitment checks.
