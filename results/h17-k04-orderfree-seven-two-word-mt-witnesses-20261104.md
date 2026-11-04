# K04: seven original two-word native-MT recurrence witnesses, found without assumed stage indices

**Agent 25, 4 November 2026 | Source-only positive mechanism, no K04 coupon.** A finite scan of **139 independently retained 16-byte source blocks**, including all 132 intact printer packets but **excluding selected copied 18:02 ACK2**, finds **seven original source triplets** satisfying two exact adjacent MT19937 native recurrence equations. All seven use 32-bit **little-endian** MT-untempered words; all other seven A/B/C endian assignments have zero matches. This strengthens the empirical basis of the existing p951 printer-source model without producing any authenticated K04 target bit or Emily K08 final caption word.

## Independent source-only discriminant

MT19937 recurrence on native untempered 32-bit words:

```
X[t+624] = X[t+397] XOR twist(X[t],X[t+1])
twist(a,b) = (((a&0x80000000)|(b&0x7fffffff))>>1)
             XOR (0x9908b0df if (b&1) else 0).
```

For any **whole 16-byte historical source block A**, take each of its two possible adjacent 3-word spans. For independent block B take each of its three possible two-word spans. Construct the precise expected two-word C span from the recurrence, and seek that span anywhere within an **independent** historical block C. Search does **not** use any row-number differences, preassigned p951 `STARTS`, acceptance hash, selected ACK, source pseudorandom seed or copied coupon.

Source corpus is the SHA256-pinned original spool (132 nondisputed original payloads) plus seven preserved complete value carriers K01, K02 telemetry prehash, K05 selected recorder quartet, K06 page strips, K07 checkpoint prehash, recorded route mask and desk nonce. Three independent 32-bit endian choices (A, B, C) give eight model families and **115,092 tested A/B-pair/position proposals per family**; each proposal checks C two-word span using a hash index. The little/little/little search returns exactly 14 *directed* matches, which fold to seven genuine unordered B/C source triplets because the XOR relation is symmetric in B and C. Other seven endian families return zero matches.

| A printer row / native word | B printer row / native word | C printer row / native word | Pre-existing p951 stage triple |
|---|---|---|---|
| 8 / 0 | 62 / 1 | 92 / 2 | 64, 461, 688 |
| 11 / 0 | 65 / 0 | 95 / 2 | 88, 485, 712 |
| 12 / 0 | 66 / 1 | 96 / 2 | 95, 492, 719 |
| 21 / 1 | 74 / 0 | 105 / 1 | 165, 562, 789 |
| 22 / 1 | 75 / 0 | 106 / 0 | 171, 568, 795 |
| 32 / 0 | 84 / 2 | 115 / 0 | 237, 634, 861 |
| 42 / 0 | 95 / 1 | 126 / 2 | 314, 711, 938 |

The original p951 stages on the right were read **only after** the source-only match scan from Agent49's pre-existing `STARTS`. Every B stage is A+397, every C stage is A+624. The observation is thus a direct 64-bit, order-independent source consistency check on a source-assembled native-MT chronology; it does **not** independently verify the target stage951, the printer copier event at 18:02, the seed initialization or any original K04 bytes.

An independence-calibrated random 32-bit word null would yield roughly **2.1×10^-11** expected exact two-word matches across all eight endian-family enumerations (accounting for candidate C offsets), before deducting B/C symmetric duplicates. This heuristic random-word estimate does not establish a statistical p-value: the p951 stage model and prior research are retrospective to the same spool bytes. Exact source words and seven complete relations are independently reproducible without that model.

## Verification and target impact

[Single-file original-source SFT](../agents/agent25/k04_mt_orderfree_2word_witness_sft.py) asserts the spool SHA256, full 139-block input, 115,092 A/B proposals for each eight orientation families and the exact seven original triplets; it also reproduces a genuine independently seeded Python MT recurrence from known synthetic output. Locally executed equivalent returned seven unordered original matches, seven wrong-endian zeroes, and synthetic positive PASS. It never reads K04 original commitment, copied ACK2 or K08 materials beyond the nonce as independent original source bytes.

**Target rank is unchanged:** known p951 printer-only original source has rank15,365 and leaves all 128 selected K04 native-output bits free. These seven historical triplets occur entirely among already-preserved printer words and were **already consistent with the existing p951 model**, so they add no independent source equation or new coupon bit. For recovery, the next decisive source relation is a **future output** connected to original selected stages951..954 (e.g., +397/+624 donor) or a historically constrained seed initializer. Merely enlarging this matching enumeration will mostly reproduce the same native PRNG geometry.

The six authentic original slots remain PASS, K04/K08 remain MISSING, combined REC8/1 remains INCOMPLETE. The original archive, verifier, route, acceptance and candidate files are untouched.
