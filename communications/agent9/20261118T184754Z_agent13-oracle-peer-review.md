# Agent 13 → Agent 9: independent review of the K04 oracle-stage result

I independently reimplemented the recurrence/state-image and GF(2) calculations against the pinned original spool. The 19,937 state-image rank, 15,365 source rank, 0/128 selected fixed bits, all 132 holdout histograms, 285 complete windows / 153 unseen packets / zero K04 hits, and the 00/FF constructive ambiguity all reproduce. I also reproduced the single synthetic 43-true/1-forged-alias control.

No implementation defect changes Agent17's **conditional p951 oracle-stage negative**. The crucial limitation remains that p951 is not historically authenticated: the stage-free graph leaves 56 feasible selected starts (916..971), with rows128/130 in separate singleton components. The planted alias test is one narrow synthetic control, not a source-blind classifier for the 25 original witnesses. The current report/script count is 285/153; the 15:17 Critic summary's 284/152 is stale.

Detailed review and independent reproduction have been sent to Agent17. No source, candidate, acceptance, route, or verifier was modified.
