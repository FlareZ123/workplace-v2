# Agent 50: close the xoroshiro128++ one-sum first-pair lane

**UTC:** 2026-11-24T03:54:10.024Z
**Scope:** K04 first-pair source-gated inversion

The canonical manual workflow has now tested the one-sum xoroshiro128++ equation under both the default QF_BV solver and the single targeted explicit `simplify → bit-blast → sat` tactic.

- Run 7 ([45307963390](https://github.com/FlareZ123/workplace-v2/actions/runs/45307963390)): 101-case algebraic replay self-test passed; unseeded planted-middle solve returned UNKNOWN / timeout at 300.003s. Source matrix skipped.
- Run 8 ([45308682982](https://github.com/FlareZ123/workplace-v2/actions/runs/45308682982)): same self-test passed; the explicit bit-blast tactic also returned UNKNOWN / timeout at 300.003s. Targeted failed-job logs confirm zero candidate models and `control_pass=false`. Source matrix skipped.

This is a **liveness failure**, not a historical-source negative. No original source model, REQUESTED3 holdout, complete ACK2 coupon, or original K04 commitment was evaluated. No component or selected bit was recovered.

Per the predeclared stop rule, close this exact xoroshiro128++ first-pair one-sum lane. Do not repeat solver/backend/timeout variations. Reopen only if a materially new source constraint changes the model or independently preserved PS-0417 native spool/queue/media evidence arrives. The K01-cell BIFF8 XF idea remains a frozen conditional extraction plan until the original `mug-stock.xls` is actually supplied.

Canonical acceptance remains K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined REC8/1 INCOMPLETE. Original candidate, commitments, verifier, and evidence were not modified.
