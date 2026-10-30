# Prior-art correction, 30 October 2026

The 59 necessary-equation selected-start placements below are a narrower subset of the 67 placements reported earlier by v1 Agent28 on 30 October, using the more defensible ACK-stage-only draw floor. Agent28 later identified three original reverse-MT partial-word relations, leaving 62 necessary-equation positions. The claimed chronology ambiguity is not novel, and this report is superseded by Agent28's 20:20 UTC source certificate. Our 59 selected placements additionally fail 120 of 141 full-source recurrence checks each, consistent with the already published v1 Agent30 earliest-completion contradiction. No authentic target bits are recovered.

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
Necessary 21-equation ordered chronologies: 59/59
Full-source falsifier: every witness violates 120 of 141 geometrically forced recurrence checks
Fixed endpoints: s0=0, s132=991; selected unknown start s129=918..976
Translation class: r13,r44,r67,r97,r129,r130,r131 each shifted by 0..58 words
No original selected payload bits, state replay, producer proof or recovery key
```

The two endpoint placements were separately generated with an integer linear-programming optimizer (SciPy 1.17.0 / HiGHS), and an independent 59-case integer-feasibility check found 59/59 feasible for the fixed-endpoint necessary-equation model. The committed portable script verifies the actual certificates without trusting the optimizer.

## Interpretation and stop

This result rules out **uniqueness of the selected event's output index under the 21 equations and four-word chronological floor alone**, even when the 991-word final endpoint is imposed. **Additional original-source falsifier (same-day amendment):** Applying *every* geometrically forced untempered MT fullword recurrence (not merely the selected 21 value-coincidence equations) to each of the 59 placements produces exactly **141 checks, including 120 original-source contradictions, for every placement**. A concrete contradiction invariant across all displacements is at t=0: original r0 reverse-word0/word1 and r52 reverse-word3 predict word t624 `1AC7CC92`, whereas the intact original r83 reverse-word2 is `523B53D0`. Therefore **none of the 59 placements is a globally valid MT-output reconstruction** under the shared producer hypothesis. The 59 certificates show only the underdetermination of the *21 chosen necessary relations*. They are never candidate historical source histories. V1 Agent30 previously found the same earliest-placement t=0 contradiction; our new bound is its constructive 59-placement extension. These are **necessary-source-relationship witnesses**, not historically authenticated printer reproductions. The 59 index possibilities are not 59 different recovered coupons. Do not use the copied r129 payload or K04 acceptance hash to select the desired index.

The next worthwhile computation needs a new **original** row/epoch/index observation that breaks this seven-row translation freedom, plus physical producer/copy continuity reaching ESC-N / PS-261003-0417 / RECOVER / attempt2, 18:02 UTC. Without that, no more unanchored completion roulette or source-only generator sweeps are justified. K04 authenticated bits gained **0/128**, K08 exact final words **0**, combined REC8 acceptance **INCOMPLETE**; six previously verified slots unchanged.

## Independent strengthening after v1 Agent28: 130 fixed observed starts, 62 free selected starts

The earlier v1 Agent28 62-position result is the correct starting point. A fresh constructive observation keeps **all 130 observed ACK row starts identical** across the whole 62-case family, while varying *only* the unobserved K04 selected-event row start. This isolates the target-stage freedom rather than changing model placements of ordinary source records.

Original observations are the 21 exact reverse/little MT fullword relations and Agent28's three separately detected original masked-31-bit boundary relations; selected r129 bytes and r128/r130 REQUESTED payloads stay withheld. Use ACK events alone for a minimal four-output chronological ordering requirement. Set `s0=0`, `s132=991`, `s127=915`, `s131=984`. An integer feasible assignment exists for every other observed ACK start, satisfying all **24 original relations**. Freeze this same complete vector for all observed rows, then vary the **single** selected r129 start over `919..980`. Every one of the 62 assignments still satisfies all 24 source relations, every ACK chronological four-word floor and all four fixed anchors. All 130 observed ACK starts and all known source words remain at the same indexes throughout this comparison.

[Agent31 fixed-observed-62 source certificate](../agents/agent31/k04_ack_fixed_observed_62_sft.py) imports the previously SHA-pinned source parser, independently rediscovers Agent28's exact three boundary triples, generates the single common observed-index witness, checks 62 mutations of the missing-event index and has seeded-MT positive controls. Local execution passed. This is a **strictly stronger illustration of source-to-selected-event placement ambiguity** than a collection of 62 separately moved observed-source completions. It does not supply an authentic coupon or prove any globally consistent MT producer. Indeed the earlier 59-placement all-source MT contradiction remains a warning that source-necessary placement certificates are not valid full histories.

The target-specific missing observation is an independently attested ACK-stage draw-consumption/index record or direct original media/copy of the selected ESC-N coupon. The source 21+3 equations cannot determine this event placement even when the entire surviving ACK placement is fixed. Do not use target SHA acceptance to choose a placement. **K04 authentic gain 0/128 bits, K08 0 exact words, combined INCOMPLETE.**
