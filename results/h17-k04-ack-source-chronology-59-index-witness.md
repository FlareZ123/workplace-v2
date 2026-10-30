# H-17 K04: a 59-position source-chronology ambiguity under ACK-only reverse-word MT identities

**Agent 31, 30 October 2026. Conditional mathematical/source result; no new archive component.**

## Question and source gate

Can the original 21 full-word MT19937 recurrence coincidences in the reversed-little-endian ACK-only spool view, discovered by v2 Agent27, constrain the selected r129 event to a unique output index? This tests an *index identifiability claim* rather than another arbitrary chronology completion. The nearest antecedents are [v2 Agent27's ACK-only source chronology](../agents/agent27/memory.md) and [v1 Agent30's earliest-start min4/min6 contradictions](https://github.com/FlareZ123/workplace-v1/blob/main/agents/agent30/memory.md). V1 Agent30 explicitly found that one routine gap was free; this result makes the corresponding **selected-event index freedom** constructive.

Original source: `resources/evidence/print/spool-reconstruction.log`, SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Source rows r0..r127 are ordinary ACKs; r131 and r132 are late ACKs. The payloads of r128/r130 (REQUESTED) and **r129 (the disputed selected 18:02 ACK2)** are excluded from all source observations and equality discovery. Neither the selected payload, K04 mask, acceptance commitment nor any other slot hash is used by the test.

## Mechanism and reproducible certificate

Hypothesis only: each retained ACK payload serializes four reversed-order little-endian MT19937 32-bit outputs. Untemper the retained words and scan for exact fullword relations of the form

`X[i+624] = X[i+397] XOR twist(X[i], X[i+1])`.

This reproduces the **19 ordinary plus two late = 21** antecedent relations, counting only later rows c and nonselected ACK observations. Each relation implies two exact integer row-start offsets. Require chronological start gaps of **at least four words** across all 133 source rows; using this conservative floor even on REQUESTED entries adds restrictions to the negative result. A concrete integer start vector `BASE` meets every equality, with `s0=0`, `s132=991` and `s129=918`.

Now translate exactly these row starts by the *same integer displacement* `d`:

`r13, r44, r67, r97, r129, r130, r131`.

For **every d=0..58 inclusive**, all 21 original MT equalities remain exact, every chronological gap stays at least four, and the same endpoints `s0=0`, `s132=991` remain unchanged. The selected index becomes **`s129=918+d`**, giving 59 distinct possible event starts, 918 through 976. The freedom is a translation of a dependency component in the original recurrence-constraint graph; it is **not** a choice of arbitrary unrelated random starts.

[Single-file portable certificate and seeded-MT positive control](../agents/agent31/k04_ack_chronology_sliding_certificate_sft.py) use Python's standard library only. The certificate reparses and SHA-pins the original spool, rediscovers the 21 fullword source observations without r129, tests a genuine seeded-MT recurrence positive control, and asserts all 59 original-source equality and chronological witnesses. Local output:

```text
Synthetic seeded-MT fullword recurrence: PASS
Original fullword source relations: 21; target r129 excluded
Source-constraint-compatible historical ordered chronologies: 59/59
Fixed endpoints: s0=0, s132=991; selected unknown start s129=918..976
Translation class: r13,r44,r67,r97,r129,r130,r131 each shifted by 0..58 words
No original selected payload bits, state replay, producer proof or recovery key
```

The two endpoint placements were separately generated with an integer linear-programming optimizer (SciPy 1.17.0 / HiGHS), and an independent 59-case integer-feasibility check found 59/59 feasible for the fixed-endpoint necessary-equation model. The committed portable script verifies the actual certificates without trusting the optimizer.

## Interpretation and stop

This result rules out **uniqueness of the selected event's output index under the 21 equations and four-word chronological floor alone**, even when the 991-word final endpoint is imposed. It does **not** establish that any of these placements admits a *global MT state reproducing every original payload*. In fact, v1 Agent30 already found a full-state contradiction for one arbitrary earliest-start completion. These are **necessary-source-relationship witnesses**, not historically authenticated printer reproductions. The 59 index possibilities are not 59 different recovered coupons. Do not use the copied r129 payload or K04 acceptance hash to select the desired index.

The next worthwhile computation needs a new **original** row/epoch/index observation that breaks this seven-row translation freedom, plus physical producer/copy continuity reaching ESC-N / PS-261003-0417 / RECOVER / attempt2, 18:02 UTC. Without that, no more unanchored completion roulette or source-only generator sweeps are justified. K04 authenticated bits gained **0/128**, K08 exact final words **0**, combined REC8 acceptance **INCOMPLETE**; six previously verified slots unchanged.
